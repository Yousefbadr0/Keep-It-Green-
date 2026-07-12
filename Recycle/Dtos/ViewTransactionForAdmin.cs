namespace Recycle.Dtos
{
    public class ViewTransactionForAdmin
    {
        public string UserName { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string MachineLocation { get; set; } = string.Empty;
        public string ItemType { get; set; } = string.Empty;
        public double Weight { get; set; }
        public double CoinsEarned { get; set; }
        public double? ConfidenceScore { get; set; }
        public string? ImagePath { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
