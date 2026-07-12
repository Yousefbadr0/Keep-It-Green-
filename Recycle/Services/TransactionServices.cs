using Recycle.Data.Models;
using Recycle.Dtos;
using Recycle.Interfaces;
using Recycle.Repos;

namespace Recycle.Services
{
    public class TransactionServices
    {
        private readonly ITransaction _transaction;
        private readonly OtpServices otpServices;
       
        public TransactionServices( ITransaction transaction, OtpServices services)
        {
            this._transaction = transaction;
            otpServices = services;
            
        }

        // Server-side reward table — clients can NEVER set their own coins.
        private static readonly Dictionary<TypeOfItem, int> CoinRates = new()
        {
            { TypeOfItem.Plastic, 10 },
            { TypeOfItem.Aluminum, 15 },
        };

        public void AddTransaction(AddTransaction transaction)
        {
            if (!Enum.TryParse<TypeOfItem>(transaction.ItemType, ignoreCase: true, out var itemType)
                || !Enum.IsDefined(itemType))
            {
                throw new ArgumentException("Invalid item type. Allowed: Plastic, Aluminum.");
            }

            var coins = CoinRates[itemType];
            _transaction.AddTransaction(transaction.OtpId, itemType, transaction.Weight, coins);
        }

        /// <summary>
        /// Machine flow: the YOLO laptop submits a detection with the OTP code.
        /// Resolves the session, validates the item, computes coins server-side,
        /// and stores the transaction with AI metadata.
        /// </summary>
        public DetectionResult AddMachineDetection(MachineDetection detection)
        {
            var session = otpServices.ResolveActiveSession(detection.Otp);
            if (session == null)
                throw new InvalidOperationException("Invalid or expired OTP.");

            if (!Enum.TryParse<TypeOfItem>(detection.ItemType, ignoreCase: true, out var itemType)
                || !Enum.IsDefined(itemType))
            {
                throw new ArgumentException("Invalid item type. Allowed: Plastic, Aluminum.");
            }

            if (session.UserId is null)
                throw new InvalidOperationException("Session is not paired with a user.");

            var coins = CoinRates[itemType];
            _transaction.AddDetection(
                session.UserId, session.MachineId, itemType,
                detection.ConfidenceScore, detection.ImagePath ?? string.Empty, coins);

            return new DetectionResult
            {
                ItemType = itemType.ToString(),
                CoinsEarned = coins,
                Message = $"{itemType} accepted (+{coins} coins)."
            };
        }

        public List<ViewTransaction> GetTransactionByUserId(string userId) {
        
          var transactionn= _transaction.GetAllTransactions().Where(t=>t.UserId==userId).ToList();
            var transactions = new List<ViewTransaction>();
            foreach (var item in transactionn)
            {
                var view= new ViewTransaction
                {
                    ItemType = item.ItemType.ToString(),
                    Weight = item.Weight,
                    CoinsEarned = item.CoinsEarned,
                    CreatedAt = DateTime.SpecifyKind(item.CreatedAt, DateTimeKind.Utc)

                };
                transactions.Add(view);
            }
            return transactions;
        }

        // Paged, newest-first — the admin report stays fast no matter how many
        // transactions a machine accumulates (SQL-side ORDER BY + OFFSET/FETCH).
        public List<ViewTransactionForAdmin>GetViewTransactionForAdmins(int machineid, int page = 1, int pageSize = 200) {
            page = Math.Max(1, page);
            pageSize = Math.Clamp(pageSize, 1, 500);
            var transactionn= _transaction.GetAllTransactions()
                .Where(t=>t.MachineId==machineid)
                .OrderByDescending(t => t.CreatedAt)
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToList();
            var transactions = new List<ViewTransactionForAdmin>();
            foreach (var item in transactionn)
            {
                var view= new ViewTransactionForAdmin
                {
                    UserName = item.User.UserName ?? string.Empty,
                    Email = item.User.Email ?? string.Empty,
                    MachineLocation = item.Machine.Location,
                    ItemType = item.ItemType.ToString(),
                    Weight = item.Weight,
                    CoinsEarned = item.CoinsEarned,
                    ConfidenceScore = item.ConfidenceScore,
                    ImagePath = item.ImagePath,
                    CreatedAt = DateTime.SpecifyKind(item.CreatedAt, DateTimeKind.Utc)
                };
                transactions.Add(view);
            }
            return transactions;
        }

        // Read-only OTP check used by the machine to validate a session before detecting.
        public bool IsOtpValid(string code) => otpServices.IsActiveOtp(code);

        public void EndTransaction(int otpid) {

            var updatestatus = new UpdateStatusOfOtp
            {
                Status = StatusOtp.Finished
            };

            otpServices.UpdateOtp(updatestatus, otpid);
        
        }
        }
    }

