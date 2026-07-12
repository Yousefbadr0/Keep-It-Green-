using Recycle.Data.Models;

namespace Recycle.Interfaces
{
    public interface IReward
    {
        // Vendors
        void AddVendor(Vendor vendor);
        IQueryable<Vendor> GetVendors();
        Vendor? GetVendorById(int id);

        // Promo codes
        void AddPromo(PromoCode promo);
        IQueryable<PromoCode> GetPromos();
        PromoCode? GetPromoById(int id);
        void DecrementPromoUsage(int promoId);

        // Redemptions
        void AddRedemption(string userId, int promoId, int coins);
        /// <summary>Atomically re-checks balance + remaining usage inside one DB transaction,
        /// decrements usage, and inserts the redemption. Returns false if either check fails
        /// under concurrency (double-spend / over-redemption protection).</summary>
        bool TryRedeem(string userId, int promoId, int requiredCoins);
        IQueryable<Redemption> GetRedemptionsByUser(string userId);
        int GetTotalRedeemed(string userId);
    }
}
