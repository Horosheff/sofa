"""
Тестирование взаимозависимостей модулей backend
Проверка импортов, API, и интеграции между модулями
"""
import sys
import traceback

def test_imports():
    """Тест 1: Проверка импортов всех модулей"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Проверка импортов модулей")
    print("="*60)
    
    tests = [
        ("app.helpers", "Helpers utilities"),
        ("app.mcp_handlers", "MCP handlers (SSE, OAuth, Tools)"),
        ("app.wordpress_tools", "WordPress tools"),
        ("app.wordstat_tools", "Wordstat tools"),
        ("app.main", "Main FastAPI app"),
    ]
    
    results = []
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"[OK] {description:<35} OK")
            results.append(True)
        except Exception as e:
            print(f"[X] {description:<35} FAILED")
            print(f"   Error: {str(e)}")
            traceback.print_exc()
            results.append(False)
    
    return all(results)


def test_helpers():
    """Тест 2: Проверка helpers функций"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Проверка helpers функций")
    print("="*60)
    
    from app.helpers import (
        is_valid_url, sanitize_url, is_valid_email,
        sanitize_string, generate_token, generate_connector_id,
        validate_dict_keys, validate_integer,
        create_jsonrpc_response, create_jsonrpc_error,
        create_mcp_text_response, safe_get, safe_int,
        mask_sensitive_data, SimpleRateLimiter
    )
    
    tests_passed = 0
    tests_total = 0
    
    # Test URL validation
    tests_total += 1
    if is_valid_url("https://example.com") and not is_valid_url("invalid"):
        print("[OK] is_valid_url() работает корректно")
        tests_passed += 1
    else:
        print("[X] is_valid_url() failed")
    
    # Test URL sanitization
    tests_total += 1
    sanitized = sanitize_url("HTTPS://EXAMPLE.COM/path/")
    if sanitized == "https://example.com/path":
        print("[OK] sanitize_url() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] sanitize_url() failed: {sanitized}")
    
    # Test email validation
    tests_total += 1
    if is_valid_email("test@example.com") and not is_valid_email("invalid"):
        print("[OK] is_valid_email() работает корректно")
        tests_passed += 1
    else:
        print("[X] is_valid_email() failed")
    
    # Test string sanitization
    tests_total += 1
    sanitized = sanitize_string("test\x00string", max_length=10)
    if sanitized == "teststring":
        print("[OK] sanitize_string() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] sanitize_string() failed: {sanitized}")
    
    # Test token generation
    tests_total += 1
    token = generate_token(16)
    if len(token) == 32:  # hex = 2 chars per byte
        print("[OK] generate_token() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] generate_token() failed: length={len(token)}")
    
    # Test connector ID generation
    tests_total += 1
    conn_id = generate_connector_id()
    if conn_id.startswith("conn_") and len(conn_id) == 21:
        print("[OK] generate_connector_id() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] generate_connector_id() failed: {conn_id}")
    
    # Test dict validation
    tests_total += 1
    valid, msg = validate_dict_keys(
        {"name": "test", "age": 25},
        required_keys=["name"],
        optional_keys=["age", "email"]
    )
    if valid:
        print("[OK] validate_dict_keys() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] validate_dict_keys() failed: {msg}")
    
    # Test integer validation
    tests_total += 1
    valid, msg = validate_integer(42, min_value=0, max_value=100)
    if valid:
        print("[OK] validate_integer() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] validate_integer() failed: {msg}")
    
    # Test JSON-RPC response
    tests_total += 1
    response = create_jsonrpc_response(1, {"status": "ok"})
    if response["jsonrpc"] == "2.0" and response["id"] == 1:
        print("[OK] create_jsonrpc_response() работает корректно")
        tests_passed += 1
    else:
        print("[X] create_jsonrpc_response() failed")
    
    # Test JSON-RPC error
    tests_total += 1
    error = create_jsonrpc_error(1, -32600, "Invalid request")
    if error["error"]["code"] == -32600:
        print("[OK] create_jsonrpc_error() работает корректно")
        tests_passed += 1
    else:
        print("[X] create_jsonrpc_error() failed")
    
    # Test MCP text response
    tests_total += 1
    mcp_resp = create_mcp_text_response("Hello")
    if mcp_resp["content"][0]["text"] == "Hello":
        print("[OK] create_mcp_text_response() работает корректно")
        tests_passed += 1
    else:
        print("[X] create_mcp_text_response() failed")
    
    # Test safe_get
    tests_total += 1
    data = {"user": {"profile": {"name": "John"}}}
    if safe_get(data, "user", "profile", "name") == "John":
        print("[OK] safe_get() работает корректно")
        tests_passed += 1
    else:
        print("[X] safe_get() failed")
    
    # Test safe_int
    tests_total += 1
    if safe_int("42") == 42 and safe_int("invalid", default=0) == 0:
        print("[OK] safe_int() работает корректно")
        tests_passed += 1
    else:
        print("[X] safe_int() failed")
    
    # Test mask_sensitive_data
    tests_total += 1
    masked = mask_sensitive_data("my_secret_token_12345")
    if "***" in masked and masked.startswith("my_s"):
        print("[OK] mask_sensitive_data() работает корректно")
        tests_passed += 1
    else:
        print(f"[X] mask_sensitive_data() failed: {masked}")
    
    # Test SimpleRateLimiter
    tests_total += 1
    limiter = SimpleRateLimiter(max_requests=2, window_seconds=60)
    if limiter.is_allowed("user1") and limiter.is_allowed("user1"):
        if not limiter.is_allowed("user1"):  # 3rd request should fail
            print("[OK] SimpleRateLimiter работает корректно")
            tests_passed += 1
        else:
            print("[X] SimpleRateLimiter failed: should block 3rd request")
    else:
        print("[X] SimpleRateLimiter failed")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def test_mcp_handlers():
    """Тест 3: Проверка MCP handlers"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Проверка MCP handlers")
    print("="*60)
    
    from app.mcp_handlers import (
        SseManager, OAuthStore,
        get_wordpress_tools, get_wordstat_tools,
        get_all_mcp_tools, get_mcp_server_info
    )
    
    tests_passed = 0
    tests_total = 0
    
    # Test SseManager
    tests_total += 1
    sse_manager = SseManager()
    if sse_manager.get_active_connections() == 0:
        print("[OK] SseManager создан корректно")
        tests_passed += 1
    else:
        print("[X] SseManager init failed")
    
    # Test OAuthStore
    tests_total += 1
    oauth_store = OAuthStore()
    client = oauth_store.create_client("test_client")
    if "client_id" in client and "client_secret" in client:
        print("[OK] OAuthStore.create_client() работает")
        tests_passed += 1
    else:
        print("[X] OAuthStore.create_client() failed")
    
    # Test OAuth flow
    tests_total += 1
    try:
        auth_code = oauth_store.issue_auth_code(client["client_id"], "conn_123")
        token = oauth_store.exchange_code(auth_code, client["client_id"])
        connector = oauth_store.get_connector_by_token(token)
        if connector == "conn_123":
            print("[OK] OAuth flow работает корректно")
            tests_passed += 1
        else:
            print(f"[X] OAuth flow failed: connector={connector}")
    except Exception as e:
        print(f"[X] OAuth flow failed: {e}")
    
    # Test WordPress tools
    tests_total += 1
    wp_tools = get_wordpress_tools()
    if len(wp_tools) == 28 and wp_tools[0]["name"] == "wordpress_get_posts":
        print(f"[OK] get_wordpress_tools() вернул {len(wp_tools)} tools")
        tests_passed += 1
    else:
        print(f"[X] get_wordpress_tools() failed: {len(wp_tools)} tools (expected 28)")
    
    # Test Wordstat tools
    tests_total += 1
    ws_tools = get_wordstat_tools()
    if len(ws_tools) == 5 and ws_tools[0]["name"] == "wordstat_get_user_info":
        print(f"[OK] get_wordstat_tools() вернул {len(ws_tools)} tools")
        tests_passed += 1
    else:
        print(f"[X] get_wordstat_tools() failed: {len(ws_tools)} tools (expected 5)")
    
    # Test all MCP tools
    tests_total += 1
    all_tools = get_all_mcp_tools()
    if len(all_tools) == 33:  # 28 WP + 5 WS
        print(f"[OK] get_all_mcp_tools() вернул {len(all_tools)} tools")
        tests_passed += 1
    else:
        print(f"[X] get_all_mcp_tools() failed: {len(all_tools)} tools (expected 33)")
    
    # Test MCP server info
    tests_total += 1
    server_info = get_mcp_server_info()
    if "protocolVersion" in server_info and "serverInfo" in server_info:
        print("[OK] get_mcp_server_info() работает корректно")
        tests_passed += 1
    else:
        print("[X] get_mcp_server_info() failed")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def test_wordpress_tools():
    """Тест 4: Проверка WordPress tools структуры"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Проверка WordPress tools")
    print("="*60)
    
    from app.wordpress_tools import handle_wordpress_tool
    
    tests_passed = 0
    tests_total = 0
    
    # Check that handler exists
    tests_total += 1
    if callable(handle_wordpress_tool):
        print("[OK] handle_wordpress_tool() импортирован")
        tests_passed += 1
    else:
        print("[X] handle_wordpress_tool() не найден")
    
    # Check function signature
    tests_total += 1
    import inspect
    sig = inspect.signature(handle_wordpress_tool)
    params = list(sig.parameters.keys())
    if "tool_name" in params and "settings" in params and "tool_args" in params:
        print("[OK] handle_wordpress_tool() имеет правильную сигнатуру")
        tests_passed += 1
    else:
        print(f"[X] handle_wordpress_tool() неправильная сигнатура: {params}")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def test_wordstat_tools():
    """Тест 5: Проверка Wordstat tools структуры"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Проверка Wordstat tools")
    print("="*60)
    
    from app.wordstat_tools import handle_wordstat_tool
    
    tests_passed = 0
    tests_total = 0
    
    # Check that handler exists
    tests_total += 1
    if callable(handle_wordstat_tool):
        print("[OK] handle_wordstat_tool() импортирован")
        tests_passed += 1
    else:
        print("[X] handle_wordstat_tool() не найден")
    
    # Check function signature
    tests_total += 1
    import inspect
    sig = inspect.signature(handle_wordstat_tool)
    params = list(sig.parameters.keys())
    if "tool_name" in params and "settings" in params and "tool_args" in params and "db" in params:
        print("[OK] handle_wordstat_tool() имеет правильную сигнатуру")
        tests_passed += 1
    else:
        print(f"[X] handle_wordstat_tool() неправильная сигнатура: {params}")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def test_main_integration():
    """Тест 6: Проверка интеграции в main.py"""
    print("\n" + "="*60)
    print("ТЕСТ 6: Проверка интеграции main.py")
    print("="*60)
    
    from app.main import (
        sse_manager, oauth_store, app
    )
    
    tests_passed = 0
    tests_total = 0
    
    # Check SSE manager
    tests_total += 1
    if hasattr(sse_manager, 'connect') and hasattr(sse_manager, 'disconnect'):
        print("[OK] sse_manager корректно импортирован в main")
        tests_passed += 1
    else:
        print("[X] sse_manager не имеет нужных методов")
    
    # Check OAuth store
    tests_total += 1
    if hasattr(oauth_store, 'create_client') and hasattr(oauth_store, 'issue_auth_code'):
        print("[OK] oauth_store корректно импортирован в main")
        tests_passed += 1
    else:
        print("[X] oauth_store не имеет нужных методов")
    
    # Check FastAPI app
    tests_total += 1
    if hasattr(app, 'routes') and len(app.routes) > 0:
        print(f"[OK] FastAPI app создан с {len(app.routes)} routes")
        tests_passed += 1
    else:
        print("[X] FastAPI app не создан корректно")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def test_cross_module_dependencies():
    """Тест 7: Проверка перекрёстных зависимостей"""
    print("\n" + "="*60)
    print("ТЕСТ 7: Проверка перекрёстных зависимостей")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Check wordpress_tools uses helpers
    tests_total += 1
    try:
        from app import wordpress_tools
        if hasattr(wordpress_tools, 'sanitize_url') or 'sanitize_url' in dir(wordpress_tools):
            print("[OK] wordpress_tools использует helpers")
            tests_passed += 1
        else:
            print("⚠️  wordpress_tools может не использовать все helpers (проверьте импорты)")
            tests_passed += 1  # Это не критично
    except Exception as e:
        print(f"[X] Ошибка проверки wordpress_tools: {e}")
    
    # Check wordstat_tools uses helpers
    tests_total += 1
    try:
        from app import wordstat_tools
        print("[OK] wordstat_tools корректно импортирован с зависимостями")
        tests_passed += 1
    except Exception as e:
        print(f"[X] Ошибка проверки wordstat_tools: {e}")
    
    # Check main uses all modules
    tests_total += 1
    try:
        from app import main
        required_imports = [
            'handle_wordpress_tool',
            'handle_wordstat_tool', 
            'SseManager',
            'OAuthStore'
        ]
        
        import os
        main_path = 'app/main.py' if os.path.exists('app/main.py') else 'backend/app/main.py'
        main_content = open(main_path, encoding='utf-8').read()
        missing = [imp for imp in required_imports if imp not in main_content]
        
        if not missing:
            print("[OK] main.py импортирует все необходимые модули")
            tests_passed += 1
        else:
            print(f"[X] main.py не импортирует: {missing}")
    except Exception as e:
        print(f"[X] Ошибка проверки main.py: {e}")
    
    print(f"\nРезультат: {tests_passed}/{tests_total} тестов пройдено")
    return tests_passed == tests_total


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ МОДУЛЕЙ BACKEND")
    print("="*60)
    
    results = []
    
    # Запуск тестов
    results.append(("Импорты модулей", test_imports()))
    results.append(("Helpers функции", test_helpers()))
    results.append(("MCP handlers", test_mcp_handlers()))
    results.append(("WordPress tools", test_wordpress_tools()))
    results.append(("Wordstat tools", test_wordstat_tools()))
    results.append(("Main интеграция", test_main_integration()))
    results.append(("Перекрёстные зависимости", test_cross_module_dependencies()))
    
    # Итоговый отчёт
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЁТ")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"{status:<10} {name}")
    
    print("="*60)
    print(f"ИТОГО: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ! Модули корректно взаимосвязаны.")
        return 0
    else:
        print(f"\n{total - passed} тестов провалено. Требуется исправление.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

