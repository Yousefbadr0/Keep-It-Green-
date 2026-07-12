using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Recycle.Data.Models;

namespace Recycle.Data
{
    /// <summary>
    /// Applies pending migrations and seeds the required Identity roles + a default
    /// admin account. Without the "Admin"/"User" roles, every [Authorize(Roles=...)]
    /// endpoint returns 403, so this must run at startup.
    /// </summary>
    public static class SeedData
    {
        public static async Task InitializeAsync(IServiceProvider services)
        {
            using var scope = services.CreateScope();
            var sp = scope.ServiceProvider;

            // 1) Create the database / apply migrations (no manual Update-Database needed).
            var db = sp.GetRequiredService<Context>();
            await db.Database.MigrateAsync();

            // 2) Seed roles.
            var roleManager = sp.GetRequiredService<RoleManager<IdentityRole>>();
            foreach (var role in new[] { "Admin", "User" })
            {
                if (!await roleManager.RoleExistsAsync(role))
                    await roleManager.CreateAsync(new IdentityRole(role));
            }

            // 3) Seed / rotate the admin account. Email + password come from config
            //    (Seed:AdminEmail / Seed:AdminPassword) so secrets can be changed per
            //    environment without a code edit. If the admin exists with a different
            //    password, it is reset to the configured one (one-time rotation).
            var userManager = sp.GetRequiredService<UserManager<User>>();
            var config = sp.GetRequiredService<IConfiguration>();
            var adminEmail = config["Seed:AdminEmail"] ?? "admin@recycle.com";
            var adminPass = config["Seed:AdminPassword"] ?? "Admin@123";

            try
            {
                var admin = await userManager.FindByEmailAsync(adminEmail);
                if (admin is null)
                {
                    admin = new User { UserName = "admin", Email = adminEmail, EmailConfirmed = true };
                    var result = await userManager.CreateAsync(admin, adminPass);
                    if (result.Succeeded)
                        await userManager.AddToRoleAsync(admin, "Admin");
                }
                else
                {
                    // Rotate the password if it changed — RemovePassword + AddPassword
                    // needs no token provider (this app doesn't register one).
                    if (!await userManager.CheckPasswordAsync(admin, adminPass))
                    {
                        await userManager.RemovePasswordAsync(admin);
                        await userManager.AddPasswordAsync(admin, adminPass);
                    }
                    if (!await userManager.IsInRoleAsync(admin, "Admin"))
                        await userManager.AddToRoleAsync(admin, "Admin");
                }
            }
            catch
            {
                // Never let admin seeding take down app startup.
            }
        }
    }
}
