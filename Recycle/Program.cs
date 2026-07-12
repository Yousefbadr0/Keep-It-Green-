using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Recycle.Data;
using Recycle.Data.Models;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;

namespace Recycle
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.

            
            builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = null;
    });
           
            builder.Services.AddDbContext<Data.Context>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection"),
                    sql => sql.EnableRetryOnFailure()));   // resilient to transient cloud-DB blips
            builder.Services.AddIdentity<Data.Models.User, IdentityRole>(options =>
            {
                // Brute-force protection: 5 wrong passwords -> account locked for 5 minutes.
                options.Lockout.MaxFailedAccessAttempts = 5;
                options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(5);
                options.Lockout.AllowedForNewUsers = true;
            })
                .AddEntityFrameworkStores<Data.Context>();
            builder.Services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            })
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,

        ValidIssuer = builder.Configuration["jwt:Issuer"],
        ValidAudience = builder.Configuration["jwt:Audience"],

        IssuerSigningKey = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(builder.Configuration["jwt:Key"]
                ?? throw new InvalidOperationException("jwt:Key is not configured."))),

         RoleClaimType = ClaimTypes.Role
    };
});


            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen(options =>
            {
                options.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "My API",
                    Version = "v1"
                });

                options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
                {
                    Name = "Authorization",
                    Type = SecuritySchemeType.Http,
                    Scheme = "bearer",
                    BearerFormat = "JWT",
                    In = ParameterLocation.Header,
                    Description = "Enter JWT Token"
                });

                options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
            });
            builder.Services.AddScoped<Interfaces.IOtp, Repos.OtpRepo>();
            builder.Services.AddScoped<Services.OtpServices>();
                builder.Services.AddScoped<Interfaces.ITransaction, Repos.TransactionRepo>();
            builder.Services.AddScoped<Services.TransactionServices>();
            builder.Services.AddScoped<Context>();
            builder.Services.AddScoped<Interfaces.IMachinecs, Repos.MachineRepo>();
            builder.Services.AddScoped<Services.MachineServices>();
                builder.Services.AddScoped<Services.UserServices>();
            builder.Services.AddScoped<Interfaces.IReward, Repos.RewardRepo>();
            builder.Services.AddScoped<Services.RewardServices>();

            builder.Services.AddScoped<Helper.ViewMachine>();

            builder.Services.AddAuthorization();

            // CORS — allow the Flutter app / machine client / Swagger to call the API.
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowAll", p =>
                    p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod());
            });

            // Hosted environments (Azure, Render, IIS, MonsterASP) terminate HTTPS at a
            // proxy and forward HTTP to the app. Honour X-Forwarded-Proto so HTTPS is
            // detected correctly and UseHttpsRedirection never loops.
            builder.Services.Configure<ForwardedHeadersOptions>(o =>
            {
                o.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
                o.KnownIPNetworks.Clear();
                o.KnownProxies.Clear();
            });

            var app = builder.Build();
            app.UseForwardedHeaders();

            // Global safety net: any unhandled exception becomes a clean JSON 500
            // (no stack trace leaked) instead of a bare error page.
            app.UseExceptionHandler(errApp => errApp.Run(async ctx =>
            {
                ctx.Response.StatusCode = StatusCodes.Status500InternalServerError;
                ctx.Response.ContentType = "application/json";
                await ctx.Response.WriteAsync("{\"Message\":\"Unexpected server error. Please try again.\"}");
            }));

            // Serve the web front-end from wwwroot (index.html at the site root).
            // Tell browsers to always revalidate, so a redeployed theme/app is picked up
            // immediately instead of being served stale from the HTTP cache.
            app.UseDefaultFiles();
            app.UseStaticFiles(new Microsoft.AspNetCore.Builder.StaticFileOptions
            {
                OnPrepareResponse = ctx =>
                {
                    ctx.Context.Response.Headers["Cache-Control"] = "no-cache, must-revalidate";
                }
            });

            

           


           
            
            

            // Swagger enabled in all environments so testers can explore the live API.
            app.UseSwagger();
            app.UseSwaggerUI();

            app.UseHttpsRedirection();

            app.UseCors("AllowAll");

            app.UseAuthentication();
            app.UseAuthorization();

          
            app.MapControllers();

            // Apply migrations + seed roles and the default admin account.
            await SeedData.InitializeAsync(app.Services);

            app.Run();
        }
    }
}
