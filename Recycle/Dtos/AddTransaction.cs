namespace Recycle.Dtos
{
    public class AddTransaction
    {
        // The verified OTP that identifies the active user + machine session.
        public int OtpId { get; set; }

        // "Plastic" or "Aluminum" (case-insensitive).
        public string ItemType { get; set; } = string.Empty;

        // Optional — reserved for a future weight sensor. Does not affect coins.
        public double Weight { get; set; }

        // NOTE: CoinsEarned is intentionally NOT here — the server computes it
        // so a client can never award itself arbitrary coins.
    }
}
