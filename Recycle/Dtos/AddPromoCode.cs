namespace Recycle.Dtos
{
    public class AddPromoCode
    {
        public int VendorId { get; set; }
        public string Code { get; set; } = string.Empty;
        public int RequiredCoins { get; set; }
        public DateTime ExpirationDate { get; set; }
        public int UsageLimit { get; set; }
    }
}
