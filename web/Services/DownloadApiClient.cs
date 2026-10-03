using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;

namespace YTDrop.Web.Services;

public sealed class DownloadApiClient(IConfiguration configuration, HttpClient httpClient)
{
    private static readonly HashSet<string> AllowedHosts = new(StringComparer.OrdinalIgnoreCase)
    {
        "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"
    };

    private readonly string apiBaseUrl =
        (configuration["ApiBaseUrl"] ?? "http://localhost:8080").TrimEnd('/');

    public bool IsValidYouTubeUrl(string value)
        => TryGetYouTubeVideoId(value, out _);

    public bool TryGetYouTubeVideoId(string value, out string videoId)
    {
        videoId = string.Empty;
        if (!Uri.TryCreate(value.Trim(), UriKind.Absolute, out var uri)
            || uri.Scheme != Uri.UriSchemeHttps
            || uri.UserInfo.Length != 0
            || !AllowedHosts.Contains(uri.Host))
        {
            return false;
        }

        string? candidate = null;
        if (uri.Host.Equals("youtu.be", StringComparison.OrdinalIgnoreCase))
        {
            candidate = uri.AbsolutePath.Trim('/').Split('/', StringSplitOptions.RemoveEmptyEntries).FirstOrDefault();
        }
        else
        {
            var segments = uri.AbsolutePath.Split('/', StringSplitOptions.RemoveEmptyEntries);
            if (segments.Length >= 2 && segments[0] is "shorts" or "embed" or "live")
            {
                candidate = segments[1];
            }
            else
            {
                candidate = uri.Query.TrimStart('?')
                    .Split('&', StringSplitOptions.RemoveEmptyEntries)
                    .Select(part => part.Split('=', 2))
                    .Where(parts => parts.Length == 2 && parts[0] == "v")
                    .Select(parts => Uri.UnescapeDataString(parts[1]))
                    .FirstOrDefault();
            }
        }

        if (candidate?.Length != 11 || candidate.Any(character =>
                !char.IsAsciiLetterOrDigit(character) && character is not '_' and not '-'))
        {
            return false;
        }

        videoId = candidate;
        return true;
    }

    public string BuildDownloadUrl(string value, string type)
        => BuildDownloadUrl(value, type, null);

    public string BuildDownloadUrl(string value, string type, int? quality)
    {
        var endpoint = type == "audio" ? "api/download-audio/" : "api/download-video/";
        var encodedUrl = Uri.EscapeDataString(value.Trim());
        var format = type == "audio" ? "&format=mp3" : $"&quality={quality ?? 1080}";
        return $"{apiBaseUrl}/{endpoint}?url={encodedUrl}{format}";
    }

    public async Task<VideoInfo?> GetVideoInfoAsync(string value, CancellationToken cancellationToken = default)
    {
        var endpoint = $"api/video-info/?url={Uri.EscapeDataString(value.Trim())}";
        return await httpClient.GetFromJsonAsync<VideoInfo>(endpoint, cancellationToken);
    }
}

public sealed record VideoInfo(string? Id, string? Title, string? Thumbnail, int? Duration, int[] Qualities);
