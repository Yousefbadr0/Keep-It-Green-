using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Identity;
using Recycle.Dtos;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Microsoft.AspNetCore.Authorization;
using Recycle.Services;


namespace Recycle.Controllers
{
    [Route("api/[controller]")]
    [ApiController]

    public class UserController : ControllerBase
    {
        private readonly UserManager<Data.Models.User> _userManager;

        private readonly IConfiguration _configuration;

        private readonly UserServices _userService;

        private readonly Data.Context _context;

        public UserController(UserManager<Data.Models.User> userManager, IConfiguration configuration,
            UserServices userService, Data.Context context)
        {
            _userManager = userManager;
            _configuration = configuration;
            _userService = userService;
            _context = context;
        }

        // ── token helpers ────────────────────────────────────────────────────────
        private async Task<string> CreateAccessTokenAsync(Data.Models.User user)
        {
            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.Id),
                new Claim(ClaimTypes.Name, user.UserName ?? string.Empty),
            };
            foreach (var role in await _userManager.GetRolesAsync(user))
                claims.Add(new Claim(ClaimTypes.Role, role));

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuration["jwt:Key"]!));
            var token = new JwtSecurityToken(
                issuer: _configuration["jwt:Issuer"],
                audience: _configuration["jwt:Audience"],
                claims: claims,
                expires: DateTime.UtcNow.AddDays(7),      // short-ish access token …
                signingCredentials: new SigningCredentials(key, SecurityAlgorithms.HmacSha256));
            return new JwtSecurityTokenHandler().WriteToken(token);
        }

        private static string HashToken(string raw) =>
            Convert.ToBase64String(System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes(raw)));

        /// <summary>Issues a new refresh token (raw returned to the client, only its hash stored).</summary>
        private string CreateRefreshToken(string userId)
        {
            var raw = Convert.ToBase64String(System.Security.Cryptography.RandomNumberGenerator.GetBytes(48));
            _context.RefreshTokens.Add(new Data.Models.RefreshToken
            {
                UserId = userId,
                TokenHash = HashToken(raw),
                CreatedAt = DateTime.UtcNow,
                ExpiresAt = DateTime.UtcNow.AddDays(60),  // … refreshed silently for up to 60 days
            });
            _context.SaveChanges();
            return raw;
        }

        [HttpPost("Register")]

        public async Task<IActionResult> Register([FromBody] RegsiterUser model)

        {
            var user = new Data.Models.User
            {
                UserName = model.UserName,

                Email = model.Email
            };

            var result = await _userManager.CreateAsync(user, model.Password);
            if (result.Succeeded)
            {


                await _userManager.AddToRoleAsync(user, "User");

                return Ok(new { Message = "User registered successfully" });
            }


            return BadRequest(result.Errors);
        }


        [HttpPost("Login")]

        public async Task<IActionResult> Login([FromBody] LoginUser model)
        {
            var user = await _userManager.FindByEmailAsync(model.Email);

            // Brute-force protection: count failed attempts; Identity locks the account
            // after the configured maximum (see Program.cs Lockout options).
            if (user != null && await _userManager.IsLockedOutAsync(user))
                return Unauthorized(new { Message = "Too many failed attempts. Try again in a few minutes." });

            if (user != null && !await _userManager.CheckPasswordAsync(user, model.Password))
            {
                await _userManager.AccessFailedAsync(user);
                return Unauthorized(new { Message = "Invalid email or password" });
            }

            if (user != null && await _userManager.CheckPasswordAsync(user, model.Password))
            {
                await _userManager.ResetAccessFailedCountAsync(user);
                return Ok(new
                {
                    Token = await CreateAccessTokenAsync(user),
                    RefreshToken = CreateRefreshToken(user.Id),
                });
            }

            return Unauthorized(new { Message = "Invalid username or password" });
        }

        // Silent re-authentication: exchange a valid refresh token for a fresh pair.
        // ROTATION: the used token is revoked, so a stolen/replayed one dies on first reuse.
        [HttpPost("Refresh")]
        public async Task<IActionResult> Refresh([FromBody] RefreshRequest model)
        {
            if (string.IsNullOrEmpty(model?.RefreshToken))
                return Unauthorized(new { Message = "Missing refresh token" });

            var hash = HashToken(model.RefreshToken);
            var stored = _context.RefreshTokens.FirstOrDefault(t => t.TokenHash == hash);
            if (stored == null || !stored.IsActive)
                return Unauthorized(new { Message = "Invalid or expired refresh token" });

            var user = await _userManager.FindByIdAsync(stored.UserId);
            if (user == null)
                return Unauthorized(new { Message = "Unknown user" });

            stored.RevokedAt = DateTime.UtcNow;
            _context.SaveChanges();

            return Ok(new
            {
                Token = await CreateAccessTokenAsync(user),
                RefreshToken = CreateRefreshToken(user.Id),
            });
        }

        public class RefreshRequest { public string? RefreshToken { get; set; } }
        [HttpGet("Coins")]
        public async Task<IActionResult> GetCoins()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (userId == null)
            {
                return Unauthorized(new { Message = "User not authenticated" });
            }
            try
            {
                var coins = await _userService.Getcoins(userId);
                return Ok(new { Coins = coins });
            }
            catch (Exception ex)
            {
                return BadRequest(new { Message = ex.Message });
            }

        }
    }
}