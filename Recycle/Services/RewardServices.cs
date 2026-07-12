using Recycle.Data.Models;
using Recycle.Dtos;
using Recycle.Interfaces;

namespace Recycle.Services
{
    public class RewardServices
    {
        private readonly IReward _reward;
        private readonly ITransaction _transaction;

        public RewardServices(IReward reward, ITransaction transaction)
        {
            _reward = reward;
            _transaction = transaction;
        }

        // ---------- Vendors (admin) ----------
        public void AddVendor(AddVendor dto)
        {
            _reward.AddVendor(new Vendor
            {
                Name = dto.Name,
                Description = dto.Description,
                Email = dto.Email,
                IsActive = true
            });
        }

        public List<ViewVendor> GetVendors() =>
            _reward.GetVendors().Select(v => new ViewVendor
            {
                Id = v.Id,
                Name = v.Name,
                Description = v.Description,
                Email = v.Email,
                IsActive = v.IsActive
            }).ToList();

        // ---------- Promo codes ----------
        public void AddPromo(AddPromoCode dto)
        {
            var vendor = _reward.GetVendorById(dto.VendorId);
            if (vendor == null)
                throw new ArgumentException("Vendor not found.");

            _reward.AddPromo(new PromoCode
            {
                VendorId = dto.VendorId,
                Code = dto.Code,
                RequiredCoins = dto.RequiredCoins,
                ExpirationDate = dto.ExpirationDate,
                UsageLimit = dto.UsageLimit,
                RemainingUsage = dto.UsageLimit
            });
        }

        public List<ViewPromoCode> GetAvailablePromos() =>
            _reward.GetPromos()
                .Where(p => p.RemainingUsage > 0
                         && p.ExpirationDate > DateTime.UtcNow
                         && p.Vendor.IsActive)
                .Select(p => new ViewPromoCode
                {
                    Id = p.Id,
                    VendorName = p.Vendor.Name,
                    Code = p.Code,
                    RequiredCoins = p.RequiredCoins,
                    ExpirationDate = p.ExpirationDate,
                    RemainingUsage = p.RemainingUsage
                }).ToList();

        // ---------- Coin balance ----------
        // Available = total coins earned (transactions) - total coins redeemed.
        public double GetAvailableCoins(string userId)
        {
            var earned = _transaction.GetAllTransactions()
                .Where(t => t.UserId == userId)
                .Sum(t => (int?)t.CoinsEarned) ?? 0;
            var redeemed = _reward.GetTotalRedeemed(userId);
            return earned - redeemed;
        }

        // ---------- Redeem (user) ----------
        public ViewRedemption Redeem(string userId, int promoId)
        {
            var promo = _reward.GetPromoById(promoId);
            if (promo == null)
                throw new ArgumentException("Promo code not found.");
            if (promo.ExpirationDate <= DateTime.UtcNow)
                throw new InvalidOperationException("Promo code has expired.");
            if (promo.RemainingUsage <= 0)
                throw new InvalidOperationException("Promo code is fully redeemed.");

            var available = GetAvailableCoins(userId);
            if (available < promo.RequiredCoins)
                throw new InvalidOperationException(
                    $"Not enough coins. Required {promo.RequiredCoins}, available {available}.");

            // Atomic: balance + usage re-checked and committed in one DB transaction,
            // so concurrent redeems can't double-spend coins or exceed the usage limit.
            if (!_reward.TryRedeem(userId, promoId, promo.RequiredCoins))
                throw new InvalidOperationException("Redemption failed — the reward may have just sold out or your balance changed.");

            return new ViewRedemption
            {
                PromoCode = promo.Code,
                CoinsDeducted = promo.RequiredCoins,
                RemainingCoins = available - promo.RequiredCoins,
                RedemptionDate = DateTime.UtcNow,
                Status = StatusRedemption.Completed.ToString()
            };
        }

        public List<ViewRedemption> GetMyRedemptions(string userId) =>
            _reward.GetRedemptionsByUser(userId).Select(r => new ViewRedemption
            {
                PromoCode = r.PromoCode.Code,
                CoinsDeducted = r.CoinsDeducted,
                RemainingCoins = 0,
                RedemptionDate = DateTime.SpecifyKind(r.RedemptionDate, DateTimeKind.Utc),
                Status = r.Status.ToString()
            }).ToList();
    }
}
