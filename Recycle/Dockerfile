# Keep It Green backend — container image (for Render / Railway / Fly / Azure Containers)
# ---- build ----
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY Recycle.csproj ./
RUN dotnet restore Recycle.csproj
COPY . ./
RUN dotnet publish Recycle.csproj -c Release -o /app /p:UseAppHost=false

# ---- runtime ----
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app ./
# Honour the host-provided $PORT (Render/Railway); default 8080 otherwise.
ENV ASPNETCORE_ENVIRONMENT=Production
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "ASPNETCORE_URLS=http://0.0.0.0:${PORT:-8080} dotnet Recycle.dll"]
