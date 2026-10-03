using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using YTDrop.Web;
using YTDrop.Web.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddScoped<DownloadApiClient>();
builder.Services.AddScoped(_ =>
{
    var apiBaseUrl = (builder.Configuration["ApiBaseUrl"] ?? "http://localhost:8080").TrimEnd('/');
    return new HttpClient { BaseAddress = new Uri($"{apiBaseUrl}/") };
});

await builder.Build().RunAsync();
