namespace Recycle.Data.Models
{
    /// <summary>
    /// A rotating refresh token. Only the SHA-256 hash of the token is stored, so a
    /// database leak cannot be replayed. Each use revokes the row and issues a new one.
    /// </summary>
    public class RefreshToken
    {
        public int Id { get; set; }

        public string UserId { get; set; } = string.Empty;
        public User? User { get; set; }

        /// <summary>SHA-256 (Base64) of the raw token handed to the client.</summary>
        public string TokenHash { get; set; } = string.Empty;

        public DateTime CreatedAt { get; set; }
        public DateTime ExpiresAt { get; set; }
        public DateTime? RevokedAt { get; set; }

        public bool IsActive => RevokedAt == null && ExpiresAt > DateTime.UtcNow;
    }
}
