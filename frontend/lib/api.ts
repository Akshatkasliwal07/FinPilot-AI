const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8001";

type ApiOptions = RequestInit & {
  authenticated?: boolean;
};

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem("access_token");
}

export function getTokenType(): string {
  if (typeof window === "undefined") {
    return "Bearer";
  }

  return (
    localStorage.getItem("token_type") || "bearer"
  );
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export async function apiRequest<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const {
    authenticated = false,
    headers,
    ...requestOptions
  } = options;

  const token = getAccessToken();
  const tokenType = getTokenType();

  const requestHeaders: HeadersInit = {
    "Content-Type": "application/json",
    ...(headers || {}),
  };

  if (authenticated) {
    if (!token) {
      throw new Error("AUTH_REQUIRED");
    }

    requestHeaders.Authorization =
      `${tokenType} ${token}`;
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...requestOptions,
      headers: requestHeaders,
      cache: "no-store",
    }
  );

  const data = await response
    .json()
    .catch(() => null);

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("AUTH_INVALID");
    }

    throw new Error(
      data?.error ||
        data?.detail ||
        data?.message ||
        `Request failed with status ${response.status}`
    );
  }

  return data as T;
}