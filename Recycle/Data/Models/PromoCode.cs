using System.ComponentModel.DataAnnotations.Schema;

namespace Recycle.Data.Models
{
    public class PromoCode
    {
        public int Id { get; set; }

        [ForeignKey("Vendor")]
        public int VendorId { get; set; }
        public Vendor Vendor { get; set; } = null!;

        public string Code { get; set; } = string.Empty;
        public int RequiredCoins { get; set; }
        public DateTime ExpirationDate { get; set; }
        public int UsageLimit { get; set; }
        public int RemainingUsage { get; set; }

        public virtual ICollection<Redemption> Redemptions { get; set; } = new List<Redemption>();
    }
}
