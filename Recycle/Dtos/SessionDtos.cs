namespace Recycle.Dtos
{
    /// <summary>Returned to the machine when it starts a session — drives the QR + code on screen.</summary>
    public class StartSessionResult
    {
        public string PairingCode { get; set; } = string.Empty;
        public int MachineId { get; set; }
        public string MachineName { get; set; } = string.Empty;
        public string LocationName { get; set; } = string.Empty;
        public int ExpiresInSeconds { get; set; }
    }

    /// <summary>Body the app sends to pair (scanned QR payload or typed code).</summary>
    public class PairRequest
    {
        public string Code { get; set; } = string.Empty;
    }

    /// <summary>Machine polls session status; becomes paired once a user scans/enters the code.</summary>
    public class SessionStatusDto
    {
        public bool Paired { get; set; }
        public string? UserName { get; set; }
    }
}
