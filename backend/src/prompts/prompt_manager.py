"""
提示词管理器
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class PromptManager:
    """提示词管理器类"""
    
    def __init__(self):
        self.templates = {}
        self.prompt_history = []
        self.load_templates()
    
    def load_templates(self):
        """加载提示词模板"""
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        if not os.path.exists(templates_dir):
            print(f"提示词模板目录不存在: {templates_dir}")
            return
        
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                template_name = filename[:-5]  # 移除.json后缀
                template_path = os.path.join(templates_dir, filename)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        self.templates[template_name] = template_data
                        print(f"✅ 加载提示词模板: {template_name}")
                except Exception as e:
                    print(f"❌ 加载提示词模板失败 {template_name}: {e}")
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取提示词模板"""
        return self.templates.get(template_name)
    
    def render_prompt(self, template_name: str, **kwargs) -> str:
        """渲染提示词模板"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"提示词模板不存在: {template_name}")
        
        prompt_text = template.get('prompt', '')
        
        # 替换模板变量
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, str):
                prompt_text = prompt_text.replace(placeholder, value)
            elif isinstance(value, (list, dict)):
                # 对于复杂类型，转换为字符串
                prompt_text = prompt_text.replace(placeholder, str(value))
        
        # 记录提示词使用历史
        self.log_prompt_usage(template_name, kwargs, prompt_text)
        
        return prompt_text
    
    def log_prompt_usage(self, template_name: str, variables: Dict[str, Any], rendered_prompt: str):
        """记录提示词使用历史"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'template_name': template_name,
            'variables': variables,
            'rendered_prompt': rendered_prompt[:200] + '...' if len(rendered_prompt) > 200 else rendered_prompt
        }
        self.prompt_history.append(log_entry)
        
        # 限制历史记录数量
        if len(self.prompt_history) > 1000:
            self.prompt_history = self.prompt_history[-500:]
    
    def get_prompt_history(self, template_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取提示词使用历史"""
        if template_name:
            return [entry for entry in self.prompt_history if entry['template_name'] == template_name]
        return self.prompt_history
    
    def add_template(self, template_name: str, template_data: Dict[str, Any]):
        """添加新的提示词模板"""
        self.templates[template_name] = template_data
        
        # 保存到文件
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        template_path = os.path.join(templates_dir, f"{template_name}.json")
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存提示词模板: {template_name}")
        except Exception as e:
            print(f"❌ 保存提示词模板失败 {template_name}: {e}")
    
    def list_templates(self) -> List[str]:
        """列出所有可用的提示词模板"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取提示词模板信息"""
        template = self.get_template(template_name)
        if template:
            return {
                'name': template_name,
                'description': template.get('description', ''),
                'version': template.get('version', '1.0'),
                'category': template.get('category', ''),
                'variables': template.get('variables', []),
                'usage_count': len([entry for entry in self.prompt_history if entry['template_name'] == template_name])
            }
        return None


# 全局提示词管理器实例
prompt_manager = PromptManager() 