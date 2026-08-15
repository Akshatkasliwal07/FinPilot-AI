const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8001";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
}

export async function loginUser(
  credentials: LoginRequest
): Promise<LoginResult> {
  const formData = new URLSearchParams();

  formData.append("username", credentials.email.trim());
  formData.append("password", credentials.password);

  const response = await fetch(
    `${API_BASE_URL}/users/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    }
  );

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.error ||
        data?.detail ||
        data?.message ||
        "Login failed"
    );
  }

  if (!data?.access_token) {
    throw new Error(
      "Access token was not returned by the server."
    );
  }

  return {
    access_token: data.access_token,
    token_type: data.token_type ?? "bearer",
  };
}