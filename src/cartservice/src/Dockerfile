# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ---------- build stage ----------
# Use amd64 to avoid grpc.tools ARM64 segfaults
FROM --platform=linux/amd64 mcr.microsoft.com/dotnet/sdk:10.0-preview AS builder

WORKDIR /app

# Copy project file and restore
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj

# Copy source and publish
COPY . .
RUN dotnet publish cartservice.csproj \
    -c Release \
    -a x64 \
    --self-contained true \
    -p:PublishSingleFile=true \
    -p:PublishTrimmed=false \
    -o /app

# ---------- runtime stage ----------
FROM --platform=linux/amd64 mcr.microsoft.com/dotnet/aspnet:10.0-preview

WORKDIR /app
COPY --from=builder /app .

EXPOSE 7070

ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_HTTP_PORTS=7070

USER 1000

ENTRYPOINT ["/app/cartservice"]

 
