using Recycle.Data.Models;

namespace Recycle.Interfaces
{
    public interface ITransaction
    {
        IQueryable<Transaction> GetAllTransactions();

        // Coins are computed server-side and passed in; the repo validates the OTP.
        void AddTransaction(int otpId, TypeOfItem itemType, double weight, int coins);

        // Machine flow: user + machine already resolved from the OTP, with AI metadata.
        void AddDetection(string userId, int machineId, TypeOfItem itemType,
                          double confidence, string imagePath, int coins);
    }
}
