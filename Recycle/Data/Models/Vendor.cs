namespace Recycle.Data.Models
{
    public class Vendor
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string Email { get; set; } = string.Empty;
        public bool IsActive { get; set; } = true;

        public virtual ICollection<PromoCode> PromoCodes { get; set; } = new List<PromoCode>();
    }
}
