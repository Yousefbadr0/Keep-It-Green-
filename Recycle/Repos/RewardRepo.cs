using Microsoft.EntityFrameworkCore;
using Recycle.Data;
using Recycle.Data.Models;
using Recycle.Interfaces;

namespace Recycle.Repos
{
    public class RewardRepo : IReward
    {
        private readonly Context _context;
        public RewardRepo(Context context)
        {
            _context = context;
        }

        // ---------- Vendors ----------
        public void AddVendor(Vendor vendor)
        {
            _context.Vendors.Add(vendor);
            _context.SaveChanges();
        }

        public IQueryable<Vendor> GetVendors() => _context.Vendors.AsQueryable();

        public Vendor? GetVendorById(int id) => _context.Vendors.FirstOrDefault(v => v.Id == id);

        // ---------- Promo codes ----------
        public void AddPromo(PromoCode promo)
        {
            _context.PromoCodes.Add(promo);
            _context.SaveChanges();
        }

        public IQueryable<PromoCode> GetPromos() =>
            _context.PromoCodes.Include(p => p.Vendor).AsQueryable();

        public PromoCode? GetPromoById(int id) =>
            _context.PromoCodes.Include(p => p.Vendor).FirstOrDefault(p => p.Id == id);

        public void DecrementPromoUsage(int promoId)
        {
            var promo = _context.PromoCodes.FirstOrDefault(p => p.Id == promoId);
            if (promo != null && promo.RemainingUsage > 0)
            {
                promo.RemainingUsage--;
                _context.SaveChanges();
            }
        }

        // ---------- Redemptions ----------
        /// <summary>The whole redeem operation in ONE serializable DB transaction, so two
        /// concurrent requests cannot both spend the same coins or exceed the usage limit.</summary>
        public bool TryRedeem(string userId, int promoId, int requiredCoins)
        {
            // The DbContext uses EnableRetryOnFailure (resilient cloud DB), whose retrying
            // execution strategy forbids a bare BeginTransaction — the manual transaction
            // MUST run inside strategy.Execute so a transient failure retries the whole unit.
            var strategy = _context.Database.CreateExecutionStrategy();
            return strategy.Execute(() =>
            {
                using var tx = _context.Database.BeginTransaction(System.Data.IsolationLevel.Serializable);

                // Atomic conditional decrement — 0 rows affected means the usage limit was hit.
                var taken = _context.PromoCodes
                    .Where(p => p.Id == promoId && p.RemainingUsage > 0)
                    .ExecuteUpdate(s => s.SetProperty(p => p.RemainingUsage, p => p.RemainingUsage - 1));
                if (taken == 0) { tx.Rollback(); return false; }

                // Re-check the balance INSIDE the transaction.
                var earned = _context.Transactions
                    .Where(t => t.UserId == userId).Sum(t => (int?)t.CoinsEarned) ?? 0;
                var redeemed = _context.Redemptions
                    .Where(r => r.UserId == userId && r.Status == StatusRedemption.Completed)
                    .Sum(r => (int?)r.CoinsDeducted) ?? 0;
                if (earned - redeemed < requiredCoins) { tx.Rollback(); return false; }

                // Insert via raw SQL (not the change tracker) so a strategy retry can never
                // double-insert a redemption. Interpolated values are parameterized by EF.
                _context.Database.ExecuteSql(
                    $"INSERT INTO Redemptions (UserId, PromoId, CoinsDeducted, RedemptionDate, Status) VALUES ({userId}, {promoId}, {requiredCoins}, {DateTime.UtcNow}, {(int)StatusRedemption.Completed})");

                tx.Commit();
                return true;
            });
        }

        public void AddRedemption(string userId, int promoId, int coins)
        {
            _context.Redemptions.Add(new Redemption
            {
                UserId = userId,
                PromoId = promoId,
                CoinsDeducted = coins,
                RedemptionDate = DateTime.UtcNow,
                Status = StatusRedemption.Completed
            });
            _context.SaveChanges();
        }

        public IQueryable<Redemption> GetRedemptionsByUser(string userId) =>
            _context.Redemptions.Include(r => r.PromoCode).Where(r => r.UserId == userId);

        public int GetTotalRedeemed(string userId) =>
            _context.Redemptions
                .Where(r => r.UserId == userId && r.Status == StatusRedemption.Completed)
                .Sum(r => (int?)r.CoinsDeducted) ?? 0;
    }
}
