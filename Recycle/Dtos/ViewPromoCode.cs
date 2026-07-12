namespace Recycle.Dtos
{
    public class ViewPromoCode
    {
        public int Id { get; set; }
        public string VendorName { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
        public int RequiredCoins { get; set; }
        public DateTime ExpirationDate { get; set; }
        public int RemainingUsage { get; set; }
    }
}
