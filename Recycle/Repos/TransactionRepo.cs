using Recycle.Data.Models;
using Recycle.Interfaces;
using Recycle.Data;
using Recycle.Dtos;

using Recycle.Helper;
using Microsoft.EntityFrameworkCore;

namespace Recycle.Repos
{
    public class TransactionRepo: ITransaction
    {
        private readonly Context _context;
       
        
        public TransactionRepo(Context context)
        {
            _context = context;
           
            
        }
        public IQueryable<Transaction> GetAllTransactions()
        {
            return _context.Transactions.AsQueryable().Include(t=>t.User).Include(t=>t.Machine);
        }

        public void AddTransaction(int otpId, TypeOfItem itemType, double weight, int coins)
        {
            var otp = _context.Otps.FirstOrDefault(o => o.Id == otpId);

            if (otp == null)
                throw new ArgumentException("OTP not found.");

            // The OTP must have been verified (IsUsed) and the session still open.
            if (!otp.IsUsed || otp.Status != StatusOtp.Active || otp.ExpireAt <= DateTime.UtcNow)
                throw new InvalidOperationException("OTP is not verified, or the session is closed/expired.");

            var newtransaction = new Transaction
            {
                UserId = otp.UserId ?? throw new InvalidOperationException("OTP has no user."),
                MachineId = otp.MachineId,
                ItemType = itemType,
                Weight = weight,
                CoinsEarned = coins,
                CreatedAt = DateTime.UtcNow
            };
            _context.Transactions.Add(newtransaction);
            _context.SaveChanges();
        }

        public void AddDetection(string userId, int machineId, TypeOfItem itemType,
                                 double confidence, string imagePath, int coins)
        {
            var newtransaction = new Transaction
            {
                UserId = userId,
                MachineId = machineId,
                ItemType = itemType,
                Weight = 0,                       // no weight sensor on the prototype
                CoinsEarned = coins,
                ConfidenceScore = confidence,
                ImagePath = imagePath,
                CreatedAt = DateTime.UtcNow
            };
            _context.Transactions.Add(newtransaction);
            _context.SaveChanges();
        }
    }
}
