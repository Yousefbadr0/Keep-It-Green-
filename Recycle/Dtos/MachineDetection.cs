namespace Recycle.Dtos
{
    /// <summary>
    /// Payload the recycling machine (YOLO laptop) sends after detecting an item.
    /// Authenticated by the X-Machine-Key header, not a user JWT.
    /// </summary>
    public class MachineDetection
    {
        // The OTP code the user generated in the app for this machine session.
        public string Otp { get; set; } = string.Empty;

        // "Plastic" or "Aluminum" (case-insensitive).
        public string ItemType { get; set; } = string.Empty;

        // YOLO confidence 0..1.
        public double ConfidenceScore { get; set; }

        // Path/URL of the saved capture (for the continuous-learning dataset). Optional.
        public string? ImagePath { get; set; }
    }

    /// <summary>Result returned to the machine after a successful detection.</summary>
    public class DetectionResult
    {
        public string ItemType { get; set; } = string.Empty;
        public int CoinsEarned { get; set; }
        public string Message { get; set; } = string.Empty;
    }
}
