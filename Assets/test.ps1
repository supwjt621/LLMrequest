# PowerShell script to call OpenTyphoon API
$apiKey = "sk-MJsRMwZQ1NCysKccWjbc968HJPxvoA7ijcXTvMG3X27vXy0S"
$apiUrl = "https://api.opentyphoon.ai/v1/chat/completions"

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $apiKey"
}

$body = @{
    model = "typhoon-v2.5-30b-a3b-instruct"
    messages = @(
        @{
            role = "system"
            content = "You are a helpful assistant"
        },
        @{
            role = "user"
            content = "Hello, how are you?"
        }
    )
    temperature = 0.7
    max_tokens = 256
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ContentType "application/json"

# Output the response
$response.choices[0].message.content