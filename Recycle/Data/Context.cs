

using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using System.Transactions;

namespace Recycle.Data
{
    public class Context:IdentityDbContext<Models.User>
    {
        public Context(DbContextOptions<Context> options) : base(options)
        {
           
        }

        public DbSet<Models.Machine> Machines { get; set; }
        public DbSet<Models.Transaction> Transactions { get; set; }
        public DbSet<Models.Otp> Otps { get; set; }
        public DbSet<Models.Vendor> Vendors { get; set; }
        public DbSet<Models.PromoCode> PromoCodes { get; set; }
        public DbSet<Models.Redemption> Redemptions { get; set; }
        public DbSet<Models.RefreshToken> RefreshTokens { get; set; }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);

            // Hot-path indexes (FK columns are indexed automatically by EF; these are not):
            builder.Entity<Models.Otp>().HasIndex(o => o.Code);                       // pair / status / submit lookups
            builder.Entity<Models.Redemption>().HasIndex(r => new { r.UserId, r.Status }); // balance computation
            builder.Entity<Models.RefreshToken>().HasIndex(t => t.TokenHash).IsUnique();
        }
    }
}
