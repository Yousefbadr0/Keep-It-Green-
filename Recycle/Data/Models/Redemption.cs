using System.ComponentModel.DataAnnotations.Schema;

namespace Recycle.Data.Models
{
    public class Redemption
    {
        public int Id { get; set; }

        [ForeignKey("User")]
        public string UserId { get; set; } = string.Empty;
        public User User { get; set; } = null!;

        [ForeignKey("PromoCode")]
        public int PromoId { get; set; }
        public PromoCode PromoCode { get; set; } = null!;

        public DateTime RedemptionDate { get; set; }
        public int CoinsDeducted { get; set; }
        public StatusRedemption Status { get; set; }
    }

    public enum StatusRedemption
    {
        Completed,
        Failed,
        Cancelled
    }
}
