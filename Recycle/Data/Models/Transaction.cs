using System.ComponentModel.DataAnnotations.Schema;

namespace Recycle.Data.Models
{
    
    public class Transaction
    {
        public int Id { get; set; }
        [ForeignKey("User")]
        public string UserId { get; set; } = string.Empty;

        
        
       
        public User User { get; set; } = null!;
        
        [ForeignKey("Machine")]
        public int MachineId { get; set; }

        public Machine Machine { get; set; } = null!;

        public TypeOfItem ItemType { get; set; }

        public double Weight { get; set; }

        public int CoinsEarned { get; set; }

        // AI detection metadata (null for transactions created via the user/app flow).
        // ConfidenceScore is the YOLO confidence 0..1; ImagePath is the saved capture
        // used for the continuous-learning dataset.
        public double? ConfidenceScore { get; set; }

        public string? ImagePath { get; set; }

        public DateTime CreatedAt { get; set; }
    }

   public enum TypeOfItem
    {
        Plastic,
       Aluminum,
        
    }
}
