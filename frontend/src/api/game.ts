import { createApiRequest } from './index';

// 消息类型定义
export interface GameMessage {
  id: number;
  user_id: number;
  story_id: number;
  session_id: string;
  message_type: number;
  message_type_name: string;
  sub_type?: string;
  content: string;
  structured_data?: any;
  related_entity?: number;
  related_entity_name?: string;
  location?: number;
  location_name?: string;
  game_time?: string;
  message_metadata?: any;
  created_at: string;
}

// 消息历史响应
export interface MessageHistoryResponse {
  messages: GameMessage[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// 获取故事消息历史的参数
export interface GetStoryMessagesParams {
  storyId: number;
  sessionId?: string;
  limit?: number;
  offset?: number;
}

// 游戏API类
export class GameApi {
  /**
   * 获取故事的消息历史
   */
  static async getStoryMessages(
    params: GetStoryMessagesParams,
    token: string
  ): Promise<MessageHistoryResponse> {
    console.log('🚀 [GameApi] 开始获取故事消息历史请求');
    console.log('📝 [GameApi] 请求参数:', {
      storyId: params.storyId,
      sessionId: params.sessionId || 'ALL',
      limit: params.limit || 100,
      offset: params.offset || 0
    });
    
    // 验证token
    if (!token || token.trim() === '') {
      console.error('❌ [GameApi] Token验证失败 - Token为空');
      throw new Error('认证失败：缺少访问令牌');
    }
    
    // 构建查询参数
    const searchParams = new URLSearchParams();
    if (params.sessionId) {
      searchParams.append('session_id', params.sessionId);
    }
    if (params.limit) {
      searchParams.append('limit', params.limit.toString());
    }
    if (params.offset) {
      searchParams.append('offset', params.offset.toString());
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/stories/${params.storyId}/messages${queryString ? `?${queryString}` : ''}`;
    
    try {
      const response = await createApiRequest<MessageHistoryResponse>(endpoint, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      console.log('✅ [GameApi] 获取故事消息历史成功:', {
        messageCount: response.messages.length,
        totalCount: response.total_count,
        hasMore: response.has_more
      });
      
      return response;
      
    } catch (error: any) {
      console.error('❌ [GameApi] 获取故事消息历史失败:', error);
      throw error;
    }
  }
} 