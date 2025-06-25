import { createApiRequest } from './index';

// 用户类型定义
export interface User {
  id: number;
  username: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

// 登录请求参数
export interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应数据
export interface LoginResponse {
  user: User;
  access_token: string;
  token_type: string;
}

// 注册请求参数
export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
}

// 注册响应数据
export interface RegisterResponse {
  user: User;
  message: string;
}

// 认证API类
export class AuthApi {
  /**
   * 用户登录
   */
  static async login(credentials: LoginRequest): Promise<LoginResponse> {
    return createApiRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  /**
   * 用户注册
   */
  static async register(userData: RegisterRequest): Promise<RegisterResponse> {
    return createApiRequest<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(token: string): Promise<User> {
    return createApiRequest<User>('/auth/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  /**
   * 刷新token
   */
  static async refreshToken(token: string): Promise<LoginResponse> {
    return createApiRequest<LoginResponse>('/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }
} 