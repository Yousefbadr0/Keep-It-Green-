namespace Recycle.Dtos
{
    public class ViewRedemption
    {
        public string PromoCode { get; set; } = string.Empty;
        public int CoinsDeducted { get; set; }
        public double RemainingCoins { get; set; }
        public DateTime RedemptionDate { get; set; }
        public string Status { get; set; } = string.Empty;
    }
}
