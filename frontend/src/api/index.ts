// API基础配置
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

// 通用API响应类型
export interface ApiResponse<T = any> {
  data?: T;
  detail?: string;
  message?: string;
}

// 通用API错误处理
export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

// 通用请求配置
export const createApiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // 记录请求开始
  console.log('🌐 [ApiRequest] 开始API请求:', {
    method: options.method || 'GET',
    endpoint,
    url,
    hasBody: !!options.body,
    bodyLength: options.body ? JSON.stringify(options.body).length : 0
  });
  
  // 记录请求头信息（隐藏敏感信息）
  const headers = { ...options.headers };
  const logHeaders: Record<string, any> = { ...headers };
  if (logHeaders['Authorization']) {
    const authHeader = logHeaders['Authorization'] as string;
    if (authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      logHeaders['Authorization'] = `Bearer ${token.length > 20 ? `${token.substring(0, 10)}...${token.substring(token.length - 10)}` : '***'}`;
    }
  }
  console.log('📋 [ApiRequest] 请求头:', logHeaders);
  
  try {
    const startTime = Date.now();
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      ...options,
    });

    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log('📡 [ApiRequest] 收到响应:', {
      status: response.status,
      statusText: response.statusText,
      duration: `${duration}ms`,
      ok: response.ok
    });

    if (!response.ok) {
      console.error('❌ [ApiRequest] HTTP错误响应:', {
        status: response.status,
        statusText: response.statusText,
        url,
        method: options.method || 'GET'
      });
      
      let errorData: any = {};
      try {
        errorData = await response.json();
        console.error('❌ [ApiRequest] 错误响应数据:', errorData);
      } catch (parseError) {
        console.error('❌ [ApiRequest] 无法解析错误响应:', parseError);
      }
      
      // 根据状态码提供更具体的错误信息
      let errorMessage = '';
      switch (response.status) {
        case 401:
          errorMessage = '认证失败：请重新登录';
          console.error('🔐 [ApiRequest] 401 认证错误');
          break;
        case 403:
          errorMessage = '权限不足：无法访问此资源';
          console.error('🚫 [ApiRequest] 403 权限错误');
          break;
        case 404:
          errorMessage = '资源不存在';
          console.error('🔍 [ApiRequest] 404 资源未找到');
          break;
        case 500:
          errorMessage = '服务器内部错误';
          console.error('🔧 [ApiRequest] 500 服务器错误');
          break;
        default:
          errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}`;
          console.error('❓ [ApiRequest] 其他HTTP错误');
      }
      
      throw new ApiError(errorMessage, response.status);
    }

    // 解析响应数据
    let responseData: T;
    try {
      responseData = await response.json();
      console.log('✅ [ApiRequest] 请求成功:', {
        endpoint,
        duration: `${duration}ms`,
        dataSize: JSON.stringify(responseData).length
      });
    } catch (parseError) {
      console.error('❌ [ApiRequest] 响应数据解析失败:', parseError);
      throw new ApiError('响应数据格式错误');
    }

    return responseData;
    
  } catch (error: any) {
    if (error instanceof ApiError) {
      // 重新抛出API错误
      throw error;
    }
    
    // 处理网络错误和其他异常
    console.error('❌ [ApiRequest] 请求异常:', {
      error: error.message,
      name: error.name,
      endpoint,
      url
    });
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new ApiError('网络连接失败：请检查网络连接');
    } else if (error.name === 'AbortError') {
      throw new ApiError('请求已取消');
    } else {
      throw new ApiError('请求失败：' + error.message);
    }
  }
}; 