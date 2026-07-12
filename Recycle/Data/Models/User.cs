using Microsoft.AspNetCore.Identity;

namespace Recycle.Data.Models

{
    public class User : IdentityUser
    {
        public double Coins { get; set; }

        public virtual ICollection<Transaction> Transactions { get; set; } = new List<Transaction>();
        public virtual ICollection<Otp> Otps { get; set; } = new List<Otp>();


    }
}

