#!/bin/bash
urls=(
  "https://httpbin.org/get"
  "https://jsonplaceholder.typicode.com/posts/1"
  "https://reqres.in/api/users/2"
  "https://dummyjson.com/products/1"
  "https://api.open-meteo.com/v1/forecast?latitude=23.1&longitude=113.3&current_weather=true"
  "https://openapi.biji.com/open/api/v1/resource/recall/knowledge"
  "https://api.deepseek.com/chat/completions"
)
for url in "${urls[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>&1)
  echo "$code  $url"
done
