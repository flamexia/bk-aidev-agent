import importlib
import os
import pkgutil

ALL_PLUGIN = {}


def import_all():
    """自动导入plugins目录下的所有Python模块

    该函数会遍历当前包目录下的所有.py文件（除了__init__.py），
    并自动导入这些模块，以确保所有插件都被注册到ALL_PLUGIN字典中。
    """
    # 获取当前包的路径
    current_package = __name__
    current_path = os.path.dirname(__file__)

    # 遍历当前目录下的所有模块
    for finder, name, ispkg in pkgutil.iter_modules([current_path]):
        if not ispkg:  # 只导入模块，不导入子包
            try:
                # 构造完整的模块名
                full_module_name = f"{current_package}.{name}"
                # 导入模块
                importlib.import_module(full_module_name)
                print(f"成功导入插件模块: {full_module_name}")
            except Exception as e:
                print(f"导入插件模块 {name} 失败: {e}")


def register_plugin(name, alias=None):
    """装饰器函数，用于注册插件到_ALL_PLUGIN字典中

    Args:
        name: 插件名称，将作为字典的key
        alias: 插件别名，可以是单个字符串或字符串列表/字典，将作为额外的key

    Returns:
        装饰器函数
    """

    def decorator(func):
        ALL_PLUGIN[name] = func

        if alias is not None:
            # 处理单个字符串别名
            if isinstance(alias, str):
                ALL_PLUGIN[alias] = func
            # 处理列表或字典形式的别名
            elif isinstance(alias, (list, set)):
                for alias_name in alias:
                    ALL_PLUGIN[alias_name] = func

        return func

    return decorator


# 自动导入所有插件模块
import_all()
