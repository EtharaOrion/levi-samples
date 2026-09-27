============================= test session starts ==============================
collecting ... collected 317 items

tests/components/base/test_script.py::test_script_inline PASSED          [  0%]
tests/components/base/test_script.py::test_script_src PASSED             [  0%]
tests/components/base/test_script.py::test_script_neither PASSED         [  0%]
tests/components/base/test_script.py::test_script_event_handler PASSED   [  1%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var0-display_color-render_dict0] PASSED [  1%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var1-display_color_name-render_dict1] FAILED [  1%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var2-display_shade-render_dict2] FAILED [  2%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var3-display_primary_colors-render_dict3] FAILED [  2%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var4-display_color_with_shades-render_dict4] FAILED [  2%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var5-display_nested_color_with_shades-render_dict5] FAILED [  3%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var6-display_nested_color_with_shades_v2-render_dict6] FAILED [  3%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var7-display_color_tuple-render_dict7] FAILED [  3%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var8-display_colors_set-render_dict8] FAILED [  4%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var9-<lambda>-render_dict9] FAILED [  4%]
tests/components/test_component.py::test_set_style_attrs PASSED          [  4%]
tests/components/test_component.py::test_custom_attrs PASSED             [  5%]
tests/components/test_component.py::test_create_component PASSED         [  5%]
tests/components/test_component.py::test_add_style PASSED                [  5%]
tests/components/test_component.py::test_get_imports PASSED              [  5%]
tests/components/test_component.py::test_get_custom_code PASSED          [  6%]
tests/components/test_component.py::test_get_props PASSED                [  6%]
tests/components/test_component.py::test_valid_props[-0] PASSED          [  6%]
tests/components/test_component.py::test_valid_props[test-1] PASSED      [  7%]
tests/components/test_component.py::test_valid_props[hi--13] PASSED      [  7%]
tests/components/test_component.py::test_invalid_prop_type[-bad_string] PASSED [  7%]
tests/components/test_component.py::test_invalid_prop_type[13-1] PASSED  [  8%]
tests/components/test_component.py::test_invalid_prop_type[None-1] PASSED [  8%]
tests/components/test_component.py::test_invalid_prop_type[test-number3] PASSED [  8%]
tests/components/test_component.py::test_var_props PASSED                [  9%]
tests/components/test_component.py::test_get_event_triggers PASSED       [  9%]
tests/components/test_component.py::test_component_event_trigger_arbitrary_args PASSED [  9%]
tests/components/test_component.py::test_create_custom_component PASSED  [ 10%]
tests/components/test_component.py::test_custom_component_hash PASSED    [ 10%]
tests/components/test_component.py::test_custom_component_wrapper PASSED [ 10%]
tests/components/test_component.py::test_invalid_event_handler_args PASSED [ 11%]
tests/components/test_component.py::test_get_hooks_nested PASSED         [ 11%]
tests/components/test_component.py::test_get_hooks_nested2 PASSED        [ 11%]
tests/components/test_component.py::test_unsupported_child_components[component5] PASSED [ 11%]
tests/components/test_component.py::test_unsupported_child_components[component6] PASSED [ 12%]
tests/components/test_component.py::test_component_with_only_valid_children[component5] PASSED [ 12%]
tests/components/test_component.py::test_component_with_only_valid_children[component7] PASSED [ 12%]
tests/components/test_component.py::test_format_component[component0-<Text>\n  {`hi`}\n</Text>] PASSED [ 13%]
tests/components/test_component.py::test_format_component[component1-<Box>\n  <Heading size={`md`}>\n  {`test`}\n</Heading>\n</Box>] PASSED [ 13%]
tests/test_app.py::test_default_app PASSED                               [ 13%]
tests/test_app.py::test_multiple_states_error PASSED                     [ 14%]
tests/test_app.py::test_add_page_default_route PASSED                    [ 14%]
tests/test_app.py::test_add_page_set_route PASSED                        [ 14%]
tests/test_app.py::test_add_page_set_route_dynamic PASSED                [ 15%]
tests/test_app.py::test_add_page_set_route_nested PASSED                 [ 15%]
tests/test_app.py::test_initialize_with_admin_dashboard PASSED           [ 15%]
tests/test_app.py::test_initialize_with_custom_admin_dashboard PASSED    [ 16%]
tests/test_app.py::test_initialize_admin_dashboard_with_view_overrides PASSED [ 16%]
tests/test_app.py::test_initialize_with_state PASSED                     [ 16%]
tests/test_app.py::test_set_and_get_state PASSED                         [ 17%]
tests/test_app.py::test_dynamic_var_event PASSED                         [ 17%]
tests/test_app.py::test_list_mutation_detection__plain_list[append then __setitem__] PASSED [ 17%]
tests/test_app.py::test_list_mutation_detection__plain_list[delitem then append] PASSED [ 17%]
tests/test_app.py::test_list_mutation_detection__plain_list[extend, remove, pop, clear] PASSED [ 18%]
tests/test_app.py::test_list_mutation_detection__plain_list[nested list] PASSED [ 18%]
tests/test_app.py::test_list_mutation_detection__plain_list[list in dict] PASSED [ 18%]
tests/test_app.py::test_dict_mutation_detection__plain_list[update then __setitem__] PASSED [ 19%]
tests/test_app.py::test_dict_mutation_detection__plain_list[delitem then update] PASSED [ 19%]
tests/test_app.py::test_dict_mutation_detection__plain_list[add, remove, pop] PASSED [ 19%]
tests/test_app.py::test_dict_mutation_detection__plain_list[dict in list] PASSED [ 20%]
tests/test_app.py::test_dict_mutation_detection__plain_list[nested dict] PASSED [ 20%]
tests/test_app.py::test_upload_file[FileUploadState-delta0] PASSED       [ 20%]
tests/test_app.py::test_upload_file[ChildFileUploadState-delta1] PASSED  [ 21%]
tests/test_app.py::test_upload_file[GrandChildFileUploadState-delta2] PASSED [ 21%]
tests/test_app.py::test_upload_file_without_annotation[FileUploadState] PASSED [ 21%]
tests/test_app.py::test_upload_file_without_annotation[ChildFileUploadState] PASSED [ 22%]
tests/test_app.py::test_upload_file_without_annotation[GrandChildFileUploadState] PASSED [ 22%]
tests/test_app.py::test_dynamic_route_var_route_change_completed_on_load PASSED [ 22%]
tests/test_app.py::test_process_events PASSED                            [ 23%]
tests/test_app.py::test_overlay_component[None-default_overlay_component-None] PASSED [ 23%]
tests/test_app.py::test_overlay_component[None-None-None] PASSED         [ 23%]
tests/test_app.py::test_overlay_component[None-overlay_component2-Text] PASSED [ 23%]
tests/test_app.py::test_overlay_component[State-default_overlay_component-Fragment] PASSED [ 24%]
tests/test_app.py::test_overlay_component[State-None-None] PASSED        [ 24%]
tests/test_app.py::test_overlay_component[State-overlay_component5-Text] PASSED [ 24%]
tests/test_app.py::test_overlay_component[State-<lambda>-Text] PASSED    [ 25%]
tests/test_app.py::test_app_wrap_compile_theme PASSED                    [ 25%]
tests/test_app.py::test_app_wrap_priority PASSED                         [ 25%]
tests/test_config.py::test_requires_app_name PASSED                      [ 26%]
tests/test_config.py::test_set_app_name PASSED                           [ 26%]
tests/test_config.py::test_deprecated_params[db_config] PASSED           [ 26%]
tests/test_config.py::test_deprecated_params[admin_dash] PASSED          [ 27%]
tests/test_config.py::test_deprecated_params[env_path] PASSED            [ 27%]
tests/test_config.py::test_update_from_env[APP_NAME-my_test_app] PASSED  [ 27%]
tests/test_config.py::test_update_from_env[FRONTEND_PORT-3001] PASSED    [ 28%]
tests/test_config.py::test_update_from_env[FRONTEND_PATH-/test] PASSED   [ 28%]
tests/test_config.py::test_update_from_env[BACKEND_PORT-8001] PASSED     [ 28%]
tests/test_config.py::test_update_from_env[API_URL-https://mybackend.com:8000] PASSED [ 29%]
tests/test_config.py::test_update_from_env[DEPLOY_URL-https://myfrontend.com] PASSED [ 29%]
tests/test_config.py::test_update_from_env[BACKEND_HOST-127.0.0.1] PASSED [ 29%]
tests/test_config.py::test_update_from_env[DB_URL-postgresql://user:pass@localhost:5432/db] PASSED [ 29%]
tests/test_config.py::test_update_from_env[REDIS_URL-redis://localhost:6379] PASSED [ 30%]
tests/test_config.py::test_update_from_env[TIMEOUT-600] PASSED           [ 30%]
tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-False] PASSED [ 30%]
tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-True] PASSED [ 31%]
tests/test_config.py::test_event_namespace[kwargs0-/_event] PASSED       [ 31%]
tests/test_config.py::test_event_namespace[kwargs1-/api/_event] PASSED   [ 31%]
tests/test_config.py::test_event_namespace[kwargs2-/event] PASSED        [ 32%]
tests/test_config.py::test_event_namespace[kwargs3-/event] PASSED        [ 32%]
tests/test_config.py::test_event_namespace[kwargs4-/event] PASSED        [ 32%]
tests/test_config.py::test_event_namespace[kwargs5-/_event] PASSED       [ 33%]
tests/test_config.py::test_event_namespace[kwargs6-/_event] PASSED       [ 33%]
tests/test_config.py::test_event_namespace[kwargs7-/_event] PASSED       [ 33%]
tests/test_config.py::test_replace_defaults[config_kwargs0-env_vars0-set_persistent_vars0-exp_config_values0] PASSED [ 34%]
tests/test_config.py::test_replace_defaults[config_kwargs1-env_vars1-set_persistent_vars1-exp_config_values1] PASSED [ 34%]
tests/test_config.py::test_replace_defaults[config_kwargs2-env_vars2-set_persistent_vars2-exp_config_values2] PASSED [ 34%]
tests/test_config.py::test_replace_defaults[config_kwargs3-env_vars3-set_persistent_vars3-exp_config_values3] PASSED [ 35%]
tests/test_config.py::test_replace_defaults[config_kwargs4-env_vars4-set_persistent_vars4-exp_config_values4] PASSED [ 35%]
tests/test_event.py::test_create_event PASSED                            [ 35%]
tests/test_event.py::test_call_event_handler PASSED                      [ 35%]
tests/test_event.py::test_fix_events[1-20] PASSED                        [ 36%]
tests/test_event.py::test_fix_events[1-21] PASSED                        [ 36%]
tests/test_event.py::test_fix_events[arg12-arg22] PASSED                 [ 36%]
tests/test_event.py::test_event_redirect[input0-Event("_redirect", {path:`/path`,external:false})] PASSED [ 37%]
tests/test_event.py::test_event_redirect[input1-Event("_redirect", {path:`/path`,external:true})] PASSED [ 37%]
tests/test_event.py::test_event_redirect[input2-Event("_redirect", {path:`/path`,external:false})] PASSED [ 37%]
tests/test_event.py::test_event_redirect[input3-Event("_redirect", {path:path,external:false})] PASSED [ 38%]
tests/test_event.py::test_event_console_log PASSED                       [ 38%]
tests/test_event.py::test_event_window_alert PASSED                      [ 38%]
tests/test_event.py::test_set_focus PASSED                               [ 39%]
tests/test_event.py::test_set_value PASSED                               [ 39%]
tests/test_event.py::test_remove_cookie PASSED                           [ 39%]
tests/test_event.py::test_remove_cookie_with_options PASSED              [ 40%]
tests/test_event.py::test_clear_local_storage PASSED                     [ 40%]
tests/test_event.py::test_remove_local_storage PASSED                    [ 40%]
tests/test_event.py::test_event_actions PASSED                           [ 41%]
tests/test_event.py::test_event_actions_on_state PASSED                  [ 41%]
tests/test_reflex.py::test_login_success_existing_token PASSED           [ 41%]
tests/test_reflex.py::test_login_success_on_browser PASSED               [ 41%]
tests/test_reflex.py::test_login_fail PASSED                             [ 42%]
tests/test_reflex.py::test_deploy_required_args_missing[args0] PASSED    [ 42%]
tests/test_reflex.py::test_deploy_required_args_missing[args1] PASSED    [ 42%]
tests/test_reflex.py::test_deploy_required_args_missing[args2] PASSED    [ 43%]
tests/test_reflex.py::test_deploy_required_args_missing[args3] PASSED    [ 43%]
tests/test_reflex.py::test_deploy_required_args_missing[args4] PASSED    [ 43%]
tests/test_reflex.py::test_deploy_required_args_missing[args5] PASSED    [ 44%]
tests/test_reflex.py::test_deploy_non_interactive_prepare_failed PASSED  [ 44%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args0-None] FAILED [ 44%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args1-values1] FAILED [ 45%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args2-values2] FAILED [ 45%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args3-values3] FAILED [ 45%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args4-values4] FAILED [ 46%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args5-values5] FAILED [ 46%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args6-values6] FAILED [ 46%]
tests/test_reflex.py::test_deploy_interactive_prepare_failed PASSED      [ 47%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses0-user_input_region0-user_input_envs0-i-want-this-site-None] FAILED [ 47%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses1-user_input_region1-user_input_envs1-i-want-this-site-args_patch1] FAILED [ 47%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses2-user_input_region2-user_input_envs2-suggested-key-None] FAILED [ 47%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses3-user_input_region3-user_input_envs3-suggested-key-args_patch3] FAILED [ 48%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses4-user_input_region4-user_input_envs4-i-want-this-site-None] FAILED [ 48%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses5-user_input_region5-user_input_envs5-i-want-this-site-args_patch5] FAILED [ 48%]
tests/utils/test_format.py::test_get_close_char[{-}] PASSED              [ 49%]
tests/utils/test_format.py::test_get_close_char[(-)] PASSED              [ 49%]
tests/utils/test_format.py::test_get_close_char[[-]] PASSED              [ 49%]
tests/utils/test_format.py::test_get_close_char[<->] PASSED              [ 50%]
tests/utils/test_format.py::test_get_close_char["-"] PASSED              [ 50%]
tests/utils/test_format.py::test_get_close_char['-'] PASSED              [ 50%]
tests/utils/test_format.py::test_is_wrapped[-{-False] PASSED             [ 51%]
tests/utils/test_format.py::test_is_wrapped[{wrap}-{-True] PASSED        [ 51%]
tests/utils/test_format.py::test_is_wrapped[{wrap-{-False] PASSED        [ 51%]
tests/utils/test_format.py::test_is_wrapped[{wrap}-(-False] PASSED       [ 52%]
tests/utils/test_format.py::test_is_wrapped[(wrap)-(-True] PASSED        [ 52%]
tests/utils/test_format.py::test_wrap[-{-True-1-{}] PASSED               [ 52%]
tests/utils/test_format.py::test_wrap[wrap-{-True-1-{wrap}] PASSED       [ 52%]
tests/utils/test_format.py::test_wrap[wrap-(-True-1-(wrap)] PASSED       [ 53%]
tests/utils/test_format.py::test_wrap[wrap-(-True-2-((wrap))] PASSED     [ 53%]
tests/utils/test_format.py::test_wrap[(wrap)-(-True-1-(wrap)] PASSED     [ 53%]
tests/utils/test_format.py::test_wrap[{wrap}-{-True-2-{wrap}] PASSED     [ 54%]
tests/utils/test_format.py::test_wrap[(wrap)-{-True-1-{(wrap)}] PASSED   [ 54%]
tests/utils/test_format.py::test_wrap[(wrap)-(-False-1-((wrap))] PASSED  [ 54%]
tests/utils/test_format.py::test_indent[-2-] PASSED                      [ 55%]
tests/utils/test_format.py::test_indent[hello-2-hello] PASSED            [ 55%]
tests/utils/test_format.py::test_indent[hello\nworld-2-  hello\n  world\n] PASSED [ 55%]
tests/utils/test_format.py::test_indent[hello\nworld-4-    hello\n    world\n] PASSED [ 56%]
tests/utils/test_format.py::test_indent[  hello\n  world-2-    hello\n    world\n] PASSED [ 56%]
tests/utils/test_format.py::test_to_snake_case[-] PASSED                 [ 56%]
tests/utils/test_format.py::test_to_snake_case[hello-hello] PASSED       [ 57%]
tests/utils/test_format.py::test_to_snake_case[Hello-hello] PASSED       [ 57%]
tests/utils/test_format.py::test_to_snake_case[camelCase-camel_case] PASSED [ 57%]
tests/utils/test_format.py::test_to_snake_case[camelTwoHumps-camel_two_humps] PASSED [ 58%]
tests/utils/test_format.py::test_to_snake_case[_start_with_underscore-_start_with_underscore] PASSED [ 58%]
tests/utils/test_format.py::test_to_snake_case[__start_with_double_underscore-__start_with_double_underscore] PASSED [ 58%]
tests/utils/test_format.py::test_to_camel_case[-] PASSED                 [ 58%]
tests/utils/test_format.py::test_to_camel_case[hello-hello] PASSED       [ 59%]
tests/utils/test_format.py::test_to_camel_case[Hello-Hello] PASSED       [ 59%]
tests/utils/test_format.py::test_to_camel_case[snake_case-snakeCase] PASSED [ 59%]
tests/utils/test_format.py::test_to_camel_case[snake_case_two-snakeCaseTwo] PASSED [ 60%]
tests/utils/test_format.py::test_to_title_case[-] PASSED                 [ 60%]
tests/utils/test_format.py::test_to_title_case[hello-Hello] PASSED       [ 60%]
tests/utils/test_format.py::test_to_title_case[Hello-Hello] PASSED       [ 61%]
tests/utils/test_format.py::test_to_title_case[snake_case-SnakeCase] PASSED [ 61%]
tests/utils/test_format.py::test_to_title_case[snake_case_two-SnakeCaseTwo] PASSED [ 61%]
tests/utils/test_format.py::test_to_kebab_case[-] PASSED                 [ 62%]
tests/utils/test_format.py::test_to_kebab_case[hello-hello] PASSED       [ 62%]
tests/utils/test_format.py::test_to_kebab_case[Hello-hello] PASSED       [ 62%]
tests/utils/test_format.py::test_to_kebab_case[snake_case-snake-case] PASSED [ 63%]
tests/utils/test_format.py::test_to_kebab_case[snake_case_two-snake-case-two] PASSED [ 63%]
tests/utils/test_format.py::test_format_string[-{``}] PASSED             [ 63%]
tests/utils/test_format.py::test_format_string[hello-{`hello`}] PASSED   [ 64%]
tests/utils/test_format.py::test_format_string[hello world-{`hello world`}] PASSED [ 64%]
tests/utils/test_format.py::test_format_string[hello=`world`-{`hello=\\`world\\``}] PASSED [ 64%]
tests/utils/test_format.py::test_format_var[input0-{`test`}] PASSED      [ 64%]
tests/utils/test_format.py::test_format_var[input1-{`test`}] PASSED      [ 65%]
tests/utils/test_format.py::test_format_var[input2-{test}] PASSED        [ 65%]
tests/utils/test_format.py::test_format_var[input3-{`test`}] PASSED      [ 65%]
tests/utils/test_format.py::test_format_var[input4-{`test`}] PASSED      [ 66%]
tests/utils/test_format.py::test_format_var[input5-{test}] PASSED        [ 66%]
tests/utils/test_format.py::test_format_route[-True-index] PASSED        [ 66%]
tests/utils/test_format.py::test_format_route[/-True-index] PASSED       [ 67%]
tests/utils/test_format.py::test_format_route[custom-route-True-custom-route] PASSED [ 67%]
tests/utils/test_format.py::test_format_route[custom-route-False-custom-route] PASSED [ 67%]
tests/utils/test_format.py::test_format_route[custom-route/-True-custom-route] PASSED [ 68%]
tests/utils/test_format.py::test_format_route[custom-route/-False-custom-route] PASSED [ 68%]
tests/utils/test_format.py::test_format_route[/custom-route-True-custom-route] PASSED [ 68%]
tests/utils/test_format.py::test_format_route[/custom-route-False-custom-route] PASSED [ 69%]
tests/utils/test_format.py::test_format_route[/custom_route-True-custom-route] PASSED [ 69%]
tests/utils/test_format.py::test_format_route[/custom_route-False-custom_route] PASSED [ 69%]
tests/utils/test_format.py::test_format_route[/CUSTOM_route-True-custom-route] PASSED [ 70%]
tests/utils/test_format.py::test_format_route[/CUSTOM_route-False-CUSTOM_route] PASSED [ 70%]
tests/utils/test_format.py::test_format_cond[cond-<C1>-""-{isTrue(cond) ? <C1> : ""}] PASSED [ 70%]
tests/utils/test_format.py::test_format_cond[cond-<C1>-<C2>-{isTrue(cond) ? <C1> : <C2>}] PASSED [ 70%]
tests/utils/test_format.py::test_format_prop[string-"string"] PASSED     [ 71%]
tests/utils/test_format.py::test_format_prop[{wrapped_string}-{wrapped_string}] PASSED [ 71%]
tests/utils/test_format.py::test_format_prop[True-{true}] PASSED         [ 71%]
tests/utils/test_format.py::test_format_prop[False-{false}] PASSED       [ 72%]
tests/utils/test_format.py::test_format_prop[123-{123}] PASSED           [ 72%]
tests/utils/test_format.py::test_format_prop[3.14-{3.14}] PASSED         [ 72%]
tests/utils/test_format.py::test_format_prop[prop6-{[1, 2, 3]}] PASSED   [ 73%]
tests/utils/test_format.py::test_format_prop[prop7-{["a", "b", "c"]}] PASSED [ 73%]
tests/utils/test_format.py::test_format_prop[prop8-{{"a": 1, "b": 2, "c": 3}}] PASSED [ 73%]
tests/utils/test_format.py::test_format_prop[prop9-{{"a": "foo \\"bar\\" baz"}}] PASSED [ 74%]
tests/utils/test_format.py::test_format_prop[prop10-{{"a": "foo \\"{ \\"bar\\" }\\" baz", "b": val}}] PASSED [ 74%]
tests/utils/test_format.py::test_format_prop[prop11-{(_e) => addEvents([Event("mock_event", {})], (_e), {})}] PASSED [ 74%]
tests/utils/test_format.py::test_format_prop[prop12-{(_e) => addEvents([Event("mock_event", {arg:_e.target.value})], (_e), {})}] PASSED [ 75%]
tests/utils/test_format.py::test_format_prop[prop13-{(_e) => addEvents([Event("mock_event", {})], (_e), {"stopPropagation": true})}] PASSED [ 75%]
tests/utils/test_format.py::test_format_prop[prop14-{(_e) => addEvents([Event("mock_event", {})], (_e), {"preventDefault": true})}] PASSED [ 75%]
tests/utils/test_format.py::test_format_prop[prop15-{{"a": "red", "b": "blue"}}] PASSED [ 76%]
tests/utils/test_format.py::test_format_prop[prop16-{var}] PASSED        [ 76%]
tests/utils/test_format.py::test_format_prop[prop17-{_}] PASSED          [ 76%]
tests/utils/test_format.py::test_format_prop[prop18-{state.colors["a"]}] PASSED [ 76%]
tests/utils/test_format.py::test_format_prop[prop19-{{"a": val}}] PASSED [ 77%]
tests/utils/test_format.py::test_format_prop[prop20-{{"a": "val"}}] PASSED [ 77%]
tests/utils/test_format.py::test_format_prop[prop21-{{"a": state.colors["val"]}}] PASSED [ 77%]
tests/utils/test_format.py::test_format_prop[prop22-{{"h1": ({node, ...props}) => <Heading {...props} as={`h1`} />}}] PASSED [ 78%]
tests/utils/test_format.py::test_format_props[single_props0-key_value_props0-output0] PASSED [ 78%]
tests/utils/test_format.py::test_get_handler_parts[input0-output0] PASSED [ 78%]
tests/utils/test_format.py::test_format_event_handler[input0-test_state.do_something] PASSED [ 79%]
tests/utils/test_format.py::test_format_event_handler[input1-test_state.child_state.change_both] PASSED [ 79%]
tests/utils/test_format.py::test_format_event_handler[input2-test_state.child_state.grandchild_state.do_nothing] PASSED [ 79%]
tests/utils/test_format.py::test_format_event[input0-Event("mock_event", {})] PASSED [ 80%]
tests/utils/test_format.py::test_format_event_chain[input0-addEvents([Event("mock_event", {}),Event("mock_event", {})])] PASSED [ 80%]
tests/utils/test_format.py::test_format_event_chain[input1-addEvents([Event("mock_event", {}),Event("mock_event", {})])] PASSED [ 80%]
tests/utils/test_format.py::test_format_query_params[input0-output0] PASSED [ 81%]
tests/utils/test_format.py::test_format_query_params[input1-output1] PASSED [ 81%]
tests/utils/test_format.py::test_format_state[input0-output0] PASSED     [ 81%]
tests/utils/test_format.py::test_format_state[input1-output1] PASSED     [ 82%]
tests/utils/test_format.py::test_format_ref[input1-ref_input1] PASSED    [ 82%]
tests/utils/test_format.py::test_format_ref[input 1-ref_input_1] PASSED  [ 82%]
tests/utils/test_format.py::test_format_ref[input-1-ref_input_1] PASSED  [ 82%]
tests/utils/test_format.py::test_format_ref[input_1-ref_input_1] PASSED  [ 83%]
tests/utils/test_format.py::test_format_ref[a long test?1! name-ref_a_long_test_1_name] PASSED [ 83%]
tests/utils/test_format.py::test_format_array_ref[input0-refs_my_array] PASSED [ 83%]
tests/utils/test_format.py::test_format_array_ref[input1-refs_my_array[0]] PASSED [ 84%]
tests/utils/test_format.py::test_format_array_ref[input2-refs_my_array[1]] PASSED [ 84%]
tests/utils/test_format.py::test_format_breadcrumbs[/foo-output0] PASSED [ 84%]
tests/utils/test_format.py::test_format_breadcrumbs[/foo/bar-output1] PASSED [ 85%]
tests/utils/test_format.py::test_format_breadcrumbs[/foo/bar/baz-output2] PASSED [ 85%]
tests/utils/test_format.py::test_format_library_name[library@^0.1.2-library] PASSED [ 85%]
tests/utils/test_format.py::test_format_library_name[library-library] PASSED [ 86%]
tests/utils/test_format.py::test_format_library_name[@library@^0.1.2-@library] PASSED [ 86%]
tests/utils/test_format.py::test_format_library_name[@library-@library] PASSED [ 86%]
tests/utils/test_format.py::test_json_dumps[None-null] PASSED            [ 87%]
tests/utils/test_format.py::test_json_dumps[True-true] PASSED            [ 87%]
tests/utils/test_format.py::test_json_dumps[1-1] PASSED                  [ 87%]
tests/utils/test_format.py::test_json_dumps[1.0-1.0] PASSED              [ 88%]
tests/utils/test_format.py::test_json_dumps[input4-[]] PASSED            [ 88%]
tests/utils/test_format.py::test_json_dumps[input5-[1, 2, 3]] PASSED     [ 88%]
tests/utils/test_format.py::test_json_dumps[input6-{}] PASSED            [ 88%]
tests/utils/test_format.py::test_json_dumps[input7-{"k1": false, "k2": true}] PASSED [ 89%]
tests/utils/test_format.py::test_json_dumps[input8-["1 day, 0:00:01.000001", "1 day, 0:00:01.000002"]] PASSED [ 89%]
tests/utils/test_format.py::test_json_dumps[input9-{"key1": "1 day, 0:00:01.000001", "key2": "1 day, 0:00:01.000002"}] PASSED [ 89%]
tests/utils/test_hosting.py::test_get_existing_access_token_and_no_invitation_code PASSED [ 90%]
tests/utils/test_hosting.py::test_get_existing_access_token_and_invitation_code PASSED [ 90%]
tests/utils/test_hosting.py::test_no_existing_access_token PASSED        [ 90%]
tests/utils/test_hosting.py::test_no_config_file PASSED                  [ 91%]
tests/utils/test_hosting.py::test_empty_config_file PASSED               [ 91%]
tests/utils/test_hosting.py::test_invalid_json_config_file PASSED        [ 91%]
tests/utils/test_hosting.py::test_validate_token_success PASSED          [ 92%]
tests/utils/test_hosting.py::test_invalid_token_access_denied PASSED     [ 92%]
tests/utils/test_hosting.py::test_unable_to_validate_token PASSED        [ 92%]
tests/utils/test_hosting.py::test_delete_access_token_from_config PASSED [ 93%]
tests/utils/test_hosting.py::test_save_access_token_and_invitation_code_to_config PASSED [ 93%]
tests/utils/test_hosting.py::test_save_access_code_but_none_invitation_code_to_config PASSED [ 93%]
tests/utils/test_hosting.py::test_authenticated_token_success PASSED     [ 94%]
tests/utils/test_hosting.py::test_no_authenticated_token PASSED          [ 94%]
tests/utils/test_hosting.py::test_maybe_authenticated_token_is_invalid PASSED [ 94%]
tests/utils/test_hosting.py::test_prepare_deploy_not_authenticated PASSED [ 94%]
tests/utils/test_hosting.py::test_server_unable_to_prepare_deploy PASSED [ 95%]
tests/utils/test_hosting.py::test_prepare_deploy_success PASSED          [ 95%]
tests/utils/test_hosting.py::test_deploy PASSED                          [ 95%]
tests/utils/test_hosting.py::test_validate_token_with_retries_failed PASSED [ 96%]
tests/utils/test_hosting.py::test_validate_token_with_retries_access_denied PASSED [ 96%]
tests/utils/test_hosting.py::test_validate_token_with_retries_success PASSED [ 96%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response0-expected0] PASSED [ 97%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response1-expected1] PASSED [ 97%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response2-expected2] PASSED [ 97%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_input_accepted PASSED [ 98%]
tests/utils/test_hosting.py::test_process_envs PASSED                    [ 98%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs0-expected0] PASSED [ 98%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs1-expected1] PASSED [ 99%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs2-expected2] PASSED [ 99%]
tests/utils/test_hosting.py::test_requirements_txt_only_contains_reflex PASSED [ 99%]
tests/utils/test_hosting.py::test_requirements_txt_only_contains_other_packages PASSED [100%]

=================================== FAILURES ===================================
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/components/layout/test_foreach.py:185: AssertionError: assert 'i' not in {'i'}
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:161: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
/home/reflex/tests/test_reflex.py:386: AttributeError: 'NoneType' object has no attribute 'kwargs'
==================================== PASSES ====================================
_____________________ test_initialize_with_admin_dashboard _____________________
----------------------------- Captured stdout call -----------------------------
Warning: Database is not initialized, run reflex db init first.
_____________ test_initialize_admin_dashboard_with_view_overrides ______________
----------------------------- Captured stdout call -----------------------------
Warning: Database is not initialized, run reflex db init first.
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-4' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-6' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-7' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-9' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-10' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-12' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-13' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-14' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-15' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-17' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-18' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-19' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-21' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-22' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-23' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-25' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-26' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-27' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-29' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-30' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-32' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-33' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-34' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-36' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-37' coro=<<async_generator_athrow without __name__>()>>
---------------------------- Captured log teardown -----------------------------
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-39' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-40' coro=<<async_generator_athrow without __name__>()>>
ERROR    asyncio:base_events.py:1758 Task was destroyed but it is pending!
task: <Task pending name='Task-41' coro=<<async_generator_athrow without __name__>()>>
_________________________ test_app_wrap_compile_theme __________________________
----------------------------- Captured stdout call -----------------------------
Compiling:  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 1/1 0:00:00
____________________________ test_app_wrap_priority ____________________________
----------------------------- Captured stdout call -----------------------------
Compiling:  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 2/2 0:00:00
__________________ test_update_from_env[APP_NAME-my_test_app] __________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value app_name with env var APP_NAME=my_test_app
___________________ test_update_from_env[FRONTEND_PORT-3001] ___________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value frontend_port with env var FRONTEND_PORT=3001
__________________ test_update_from_env[FRONTEND_PATH-/test] ___________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value frontend_path with env var FRONTEND_PATH=/test
___________________ test_update_from_env[BACKEND_PORT-8001] ____________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value backend_port with env var BACKEND_PORT=8001
___________ test_update_from_env[API_URL-https://mybackend.com:8000] ___________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value api_url with env var 
API_URL=https://mybackend.com:8000
___________ test_update_from_env[DEPLOY_URL-https://myfrontend.com] ____________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value deploy_url with env var 
DEPLOY_URL=https://myfrontend.com
_________________ test_update_from_env[BACKEND_HOST-127.0.0.1] _________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value backend_host with env var BACKEND_HOST=127.0.0.1
____________ test_update_from_env[REDIS_URL-redis://localhost:6379] ____________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value redis_url with env var 
REDIS_URL=redis://localhost:6379
______________________ test_update_from_env[TIMEOUT-600] _______________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value timeout with env var TIMEOUT=600
________________ test_update_from_env[TELEMETRY_ENABLED-False] _________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value telemetry_enabled with env var 
TELEMETRY_ENABLED=False
_________________ test_update_from_env[TELEMETRY_ENABLED-True] _________________
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value telemetry_enabled with env var 
TELEMETRY_ENABLED=True
_ test_replace_defaults[config_kwargs2-env_vars2-set_persistent_vars2-exp_config_values2] _
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value backend_port with env var BACKEND_PORT=8002
_ test_replace_defaults[config_kwargs3-env_vars3-set_persistent_vars3-exp_config_values3] _
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value backend_port with env var BACKEND_PORT=8002
_ test_replace_defaults[config_kwargs4-env_vars4-set_persistent_vars4-exp_config_values4] _
----------------------------- Captured stdout call -----------------------------
Info: Overriding config value backend_port with env var BACKEND_PORT=8002
_____________________ test_server_unable_to_prepare_deploy _____________________
----------------------------- Captured stdout call -----------------------------
Server did not respond with valid json: Expecting value: line 1 column 1 (char 
0)
________________ test_validate_token_with_retries_access_denied ________________
----------------------------- Captured stdout call -----------------------------
Access denied
_ test_interactive_get_deployment_key_user_accepts_defaults[prepare_response1-expected1] _
----------------------------- Captured stdout call -----------------------------
Overwrite deployment [ key21 ] ...
_____________ test_interactive_prompt_for_envs[inputs0-expected0] ______________
----------------------------- Captured stdout call -----------------------------
Environment variables for your production App ...
Finished adding envs.
_____________ test_interactive_prompt_for_envs[inputs1-expected1] ______________
----------------------------- Captured stdout call -----------------------------
Environment variables for your production App ...
No envs added. Continuing ...
_____________ test_interactive_prompt_for_envs[inputs2-expected2] ______________
----------------------------- Captured stdout call -----------------------------
Environment variables for your production App ...
Finished adding envs.
=========================== short test summary info ============================
PASSED tests/components/base/test_script.py::test_script_inline
PASSED tests/components/base/test_script.py::test_script_src
PASSED tests/components/base/test_script.py::test_script_neither
PASSED tests/components/base/test_script.py::test_script_event_handler
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var0-display_color-render_dict0]
PASSED tests/components/test_component.py::test_set_style_attrs
PASSED tests/components/test_component.py::test_custom_attrs
PASSED tests/components/test_component.py::test_create_component
PASSED tests/components/test_component.py::test_add_style
PASSED tests/components/test_component.py::test_get_imports
PASSED tests/components/test_component.py::test_get_custom_code
PASSED tests/components/test_component.py::test_get_props
PASSED tests/components/test_component.py::test_valid_props[-0]
PASSED tests/components/test_component.py::test_valid_props[test-1]
PASSED tests/components/test_component.py::test_valid_props[hi--13]
PASSED tests/components/test_component.py::test_invalid_prop_type[-bad_string]
PASSED tests/components/test_component.py::test_invalid_prop_type[13-1]
PASSED tests/components/test_component.py::test_invalid_prop_type[None-1]
PASSED tests/components/test_component.py::test_invalid_prop_type[test-number3]
PASSED tests/components/test_component.py::test_var_props
PASSED tests/components/test_component.py::test_get_event_triggers
PASSED tests/components/test_component.py::test_component_event_trigger_arbitrary_args
PASSED tests/components/test_component.py::test_create_custom_component
PASSED tests/components/test_component.py::test_custom_component_hash
PASSED tests/components/test_component.py::test_custom_component_wrapper
PASSED tests/components/test_component.py::test_invalid_event_handler_args
PASSED tests/components/test_component.py::test_get_hooks_nested
PASSED tests/components/test_component.py::test_get_hooks_nested2
PASSED tests/components/test_component.py::test_unsupported_child_components[component5]
PASSED tests/components/test_component.py::test_unsupported_child_components[component6]
PASSED tests/components/test_component.py::test_component_with_only_valid_children[component5]
PASSED tests/components/test_component.py::test_component_with_only_valid_children[component7]
PASSED tests/components/test_component.py::test_format_component[component0-<Text>\n  {`hi`}\n</Text>]
PASSED tests/components/test_component.py::test_format_component[component1-<Box>\n  <Heading size={`md`}>\n  {`test`}\n</Heading>\n</Box>]
PASSED tests/test_app.py::test_default_app
PASSED tests/test_app.py::test_multiple_states_error
PASSED tests/test_app.py::test_add_page_default_route
PASSED tests/test_app.py::test_add_page_set_route
PASSED tests/test_app.py::test_add_page_set_route_dynamic
PASSED tests/test_app.py::test_add_page_set_route_nested
PASSED tests/test_app.py::test_initialize_with_admin_dashboard
PASSED tests/test_app.py::test_initialize_with_custom_admin_dashboard
PASSED tests/test_app.py::test_initialize_admin_dashboard_with_view_overrides
PASSED tests/test_app.py::test_initialize_with_state
PASSED tests/test_app.py::test_set_and_get_state
PASSED tests/test_app.py::test_dynamic_var_event
PASSED tests/test_app.py::test_list_mutation_detection__plain_list[append then __setitem__]
PASSED tests/test_app.py::test_list_mutation_detection__plain_list[delitem then append]
PASSED tests/test_app.py::test_list_mutation_detection__plain_list[extend, remove, pop, clear]
PASSED tests/test_app.py::test_list_mutation_detection__plain_list[nested list]
PASSED tests/test_app.py::test_list_mutation_detection__plain_list[list in dict]
PASSED tests/test_app.py::test_dict_mutation_detection__plain_list[update then __setitem__]
PASSED tests/test_app.py::test_dict_mutation_detection__plain_list[delitem then update]
PASSED tests/test_app.py::test_dict_mutation_detection__plain_list[add, remove, pop]
PASSED tests/test_app.py::test_dict_mutation_detection__plain_list[dict in list]
PASSED tests/test_app.py::test_dict_mutation_detection__plain_list[nested dict]
PASSED tests/test_app.py::test_upload_file[FileUploadState-delta0]
PASSED tests/test_app.py::test_upload_file[ChildFileUploadState-delta1]
PASSED tests/test_app.py::test_upload_file[GrandChildFileUploadState-delta2]
PASSED tests/test_app.py::test_upload_file_without_annotation[FileUploadState]
PASSED tests/test_app.py::test_upload_file_without_annotation[ChildFileUploadState]
PASSED tests/test_app.py::test_upload_file_without_annotation[GrandChildFileUploadState]
PASSED tests/test_app.py::test_dynamic_route_var_route_change_completed_on_load
PASSED tests/test_app.py::test_process_events
PASSED tests/test_app.py::test_overlay_component[None-default_overlay_component-None]
PASSED tests/test_app.py::test_overlay_component[None-None-None]
PASSED tests/test_app.py::test_overlay_component[None-overlay_component2-Text]
PASSED tests/test_app.py::test_overlay_component[State-default_overlay_component-Fragment]
PASSED tests/test_app.py::test_overlay_component[State-None-None]
PASSED tests/test_app.py::test_overlay_component[State-overlay_component5-Text]
PASSED tests/test_app.py::test_overlay_component[State-<lambda>-Text]
PASSED tests/test_app.py::test_app_wrap_compile_theme
PASSED tests/test_app.py::test_app_wrap_priority
PASSED tests/test_config.py::test_requires_app_name
PASSED tests/test_config.py::test_set_app_name
PASSED tests/test_config.py::test_deprecated_params[db_config]
PASSED tests/test_config.py::test_deprecated_params[admin_dash]
PASSED tests/test_config.py::test_deprecated_params[env_path]
PASSED tests/test_config.py::test_update_from_env[APP_NAME-my_test_app]
PASSED tests/test_config.py::test_update_from_env[FRONTEND_PORT-3001]
PASSED tests/test_config.py::test_update_from_env[FRONTEND_PATH-/test]
PASSED tests/test_config.py::test_update_from_env[BACKEND_PORT-8001]
PASSED tests/test_config.py::test_update_from_env[API_URL-https://mybackend.com:8000]
PASSED tests/test_config.py::test_update_from_env[DEPLOY_URL-https://myfrontend.com]
PASSED tests/test_config.py::test_update_from_env[BACKEND_HOST-127.0.0.1]
PASSED tests/test_config.py::test_update_from_env[DB_URL-postgresql://user:pass@localhost:5432/db]
PASSED tests/test_config.py::test_update_from_env[REDIS_URL-redis://localhost:6379]
PASSED tests/test_config.py::test_update_from_env[TIMEOUT-600]
PASSED tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-False]
PASSED tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-True]
PASSED tests/test_config.py::test_event_namespace[kwargs0-/_event]
PASSED tests/test_config.py::test_event_namespace[kwargs1-/api/_event]
PASSED tests/test_config.py::test_event_namespace[kwargs2-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs3-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs4-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs5-/_event]
PASSED tests/test_config.py::test_event_namespace[kwargs6-/_event]
PASSED tests/test_config.py::test_event_namespace[kwargs7-/_event]
PASSED tests/test_config.py::test_replace_defaults[config_kwargs0-env_vars0-set_persistent_vars0-exp_config_values0]
PASSED tests/test_config.py::test_replace_defaults[config_kwargs1-env_vars1-set_persistent_vars1-exp_config_values1]
PASSED tests/test_config.py::test_replace_defaults[config_kwargs2-env_vars2-set_persistent_vars2-exp_config_values2]
PASSED tests/test_config.py::test_replace_defaults[config_kwargs3-env_vars3-set_persistent_vars3-exp_config_values3]
PASSED tests/test_config.py::test_replace_defaults[config_kwargs4-env_vars4-set_persistent_vars4-exp_config_values4]
PASSED tests/test_event.py::test_create_event
PASSED tests/test_event.py::test_call_event_handler
PASSED tests/test_event.py::test_fix_events[1-20]
PASSED tests/test_event.py::test_fix_events[1-21]
PASSED tests/test_event.py::test_fix_events[arg12-arg22]
PASSED tests/test_event.py::test_event_redirect[input0-Event("_redirect", {path:`/path`,external:false})]
PASSED tests/test_event.py::test_event_redirect[input1-Event("_redirect", {path:`/path`,external:true})]
PASSED tests/test_event.py::test_event_redirect[input2-Event("_redirect", {path:`/path`,external:false})]
PASSED tests/test_event.py::test_event_redirect[input3-Event("_redirect", {path:path,external:false})]
PASSED tests/test_event.py::test_event_console_log
PASSED tests/test_event.py::test_event_window_alert
PASSED tests/test_event.py::test_set_focus
PASSED tests/test_event.py::test_set_value
PASSED tests/test_event.py::test_remove_cookie
PASSED tests/test_event.py::test_remove_cookie_with_options
PASSED tests/test_event.py::test_clear_local_storage
PASSED tests/test_event.py::test_remove_local_storage
PASSED tests/test_event.py::test_event_actions
PASSED tests/test_event.py::test_event_actions_on_state
PASSED tests/test_reflex.py::test_login_success_existing_token
PASSED tests/test_reflex.py::test_login_success_on_browser
PASSED tests/test_reflex.py::test_login_fail
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args0]
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args1]
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args2]
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args3]
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args4]
PASSED tests/test_reflex.py::test_deploy_required_args_missing[args5]
PASSED tests/test_reflex.py::test_deploy_non_interactive_prepare_failed
PASSED tests/test_reflex.py::test_deploy_interactive_prepare_failed
PASSED tests/utils/test_format.py::test_get_close_char[{-}]
PASSED tests/utils/test_format.py::test_get_close_char[(-)]
PASSED tests/utils/test_format.py::test_get_close_char[[-]]
PASSED tests/utils/test_format.py::test_get_close_char[<->]
PASSED tests/utils/test_format.py::test_get_close_char["-"]
PASSED tests/utils/test_format.py::test_get_close_char['-']
PASSED tests/utils/test_format.py::test_is_wrapped[-{-False]
PASSED tests/utils/test_format.py::test_is_wrapped[{wrap}-{-True]
PASSED tests/utils/test_format.py::test_is_wrapped[{wrap-{-False]
PASSED tests/utils/test_format.py::test_is_wrapped[{wrap}-(-False]
PASSED tests/utils/test_format.py::test_is_wrapped[(wrap)-(-True]
PASSED tests/utils/test_format.py::test_wrap[-{-True-1-{}]
PASSED tests/utils/test_format.py::test_wrap[wrap-{-True-1-{wrap}]
PASSED tests/utils/test_format.py::test_wrap[wrap-(-True-1-(wrap)]
PASSED tests/utils/test_format.py::test_wrap[wrap-(-True-2-((wrap))]
PASSED tests/utils/test_format.py::test_wrap[(wrap)-(-True-1-(wrap)]
PASSED tests/utils/test_format.py::test_wrap[{wrap}-{-True-2-{wrap}]
PASSED tests/utils/test_format.py::test_wrap[(wrap)-{-True-1-{(wrap)}]
PASSED tests/utils/test_format.py::test_wrap[(wrap)-(-False-1-((wrap))]
PASSED tests/utils/test_format.py::test_indent[-2-]
PASSED tests/utils/test_format.py::test_indent[hello-2-hello]
PASSED tests/utils/test_format.py::test_indent[hello\nworld-2-  hello\n  world\n]
PASSED tests/utils/test_format.py::test_indent[hello\nworld-4-    hello\n    world\n]
PASSED tests/utils/test_format.py::test_indent[  hello\n  world-2-    hello\n    world\n]
PASSED tests/utils/test_format.py::test_to_snake_case[-]
PASSED tests/utils/test_format.py::test_to_snake_case[hello-hello]
PASSED tests/utils/test_format.py::test_to_snake_case[Hello-hello]
PASSED tests/utils/test_format.py::test_to_snake_case[camelCase-camel_case]
PASSED tests/utils/test_format.py::test_to_snake_case[camelTwoHumps-camel_two_humps]
PASSED tests/utils/test_format.py::test_to_snake_case[_start_with_underscore-_start_with_underscore]
PASSED tests/utils/test_format.py::test_to_snake_case[__start_with_double_underscore-__start_with_double_underscore]
PASSED tests/utils/test_format.py::test_to_camel_case[-]
PASSED tests/utils/test_format.py::test_to_camel_case[hello-hello]
PASSED tests/utils/test_format.py::test_to_camel_case[Hello-Hello]
PASSED tests/utils/test_format.py::test_to_camel_case[snake_case-snakeCase]
PASSED tests/utils/test_format.py::test_to_camel_case[snake_case_two-snakeCaseTwo]
PASSED tests/utils/test_format.py::test_to_title_case[-]
PASSED tests/utils/test_format.py::test_to_title_case[hello-Hello]
PASSED tests/utils/test_format.py::test_to_title_case[Hello-Hello]
PASSED tests/utils/test_format.py::test_to_title_case[snake_case-SnakeCase]
PASSED tests/utils/test_format.py::test_to_title_case[snake_case_two-SnakeCaseTwo]
PASSED tests/utils/test_format.py::test_to_kebab_case[-]
PASSED tests/utils/test_format.py::test_to_kebab_case[hello-hello]
PASSED tests/utils/test_format.py::test_to_kebab_case[Hello-hello]
PASSED tests/utils/test_format.py::test_to_kebab_case[snake_case-snake-case]
PASSED tests/utils/test_format.py::test_to_kebab_case[snake_case_two-snake-case-two]
PASSED tests/utils/test_format.py::test_format_string[-{``}]
PASSED tests/utils/test_format.py::test_format_string[hello-{`hello`}]
PASSED tests/utils/test_format.py::test_format_string[hello world-{`hello world`}]
PASSED tests/utils/test_format.py::test_format_string[hello=`world`-{`hello=\\`world\\``}]
PASSED tests/utils/test_format.py::test_format_var[input0-{`test`}]
PASSED tests/utils/test_format.py::test_format_var[input1-{`test`}]
PASSED tests/utils/test_format.py::test_format_var[input2-{test}]
PASSED tests/utils/test_format.py::test_format_var[input3-{`test`}]
PASSED tests/utils/test_format.py::test_format_var[input4-{`test`}]
PASSED tests/utils/test_format.py::test_format_var[input5-{test}]
PASSED tests/utils/test_format.py::test_format_route[-True-index]
PASSED tests/utils/test_format.py::test_format_route[/-True-index]
PASSED tests/utils/test_format.py::test_format_route[custom-route-True-custom-route]
PASSED tests/utils/test_format.py::test_format_route[custom-route-False-custom-route]
PASSED tests/utils/test_format.py::test_format_route[custom-route/-True-custom-route]
PASSED tests/utils/test_format.py::test_format_route[custom-route/-False-custom-route]
PASSED tests/utils/test_format.py::test_format_route[/custom-route-True-custom-route]
PASSED tests/utils/test_format.py::test_format_route[/custom-route-False-custom-route]
PASSED tests/utils/test_format.py::test_format_route[/custom_route-True-custom-route]
PASSED tests/utils/test_format.py::test_format_route[/custom_route-False-custom_route]
PASSED tests/utils/test_format.py::test_format_route[/CUSTOM_route-True-custom-route]
PASSED tests/utils/test_format.py::test_format_route[/CUSTOM_route-False-CUSTOM_route]
PASSED tests/utils/test_format.py::test_format_cond[cond-<C1>-""-{isTrue(cond) ? <C1> : ""}]
PASSED tests/utils/test_format.py::test_format_cond[cond-<C1>-<C2>-{isTrue(cond) ? <C1> : <C2>}]
PASSED tests/utils/test_format.py::test_format_prop[string-"string"]
PASSED tests/utils/test_format.py::test_format_prop[{wrapped_string}-{wrapped_string}]
PASSED tests/utils/test_format.py::test_format_prop[True-{true}]
PASSED tests/utils/test_format.py::test_format_prop[False-{false}]
PASSED tests/utils/test_format.py::test_format_prop[123-{123}]
PASSED tests/utils/test_format.py::test_format_prop[3.14-{3.14}]
PASSED tests/utils/test_format.py::test_format_prop[prop6-{[1, 2, 3]}]
PASSED tests/utils/test_format.py::test_format_prop[prop7-{["a", "b", "c"]}]
PASSED tests/utils/test_format.py::test_format_prop[prop8-{{"a": 1, "b": 2, "c": 3}}]
PASSED tests/utils/test_format.py::test_format_prop[prop9-{{"a": "foo \\"bar\\" baz"}}]
PASSED tests/utils/test_format.py::test_format_prop[prop10-{{"a": "foo \\"{ \\"bar\\" }\\" baz", "b": val}}]
PASSED tests/utils/test_format.py::test_format_prop[prop11-{(_e) => addEvents([Event("mock_event", {})], (_e), {})}]
PASSED tests/utils/test_format.py::test_format_prop[prop12-{(_e) => addEvents([Event("mock_event", {arg:_e.target.value})], (_e), {})}]
PASSED tests/utils/test_format.py::test_format_prop[prop13-{(_e) => addEvents([Event("mock_event", {})], (_e), {"stopPropagation": true})}]
PASSED tests/utils/test_format.py::test_format_prop[prop14-{(_e) => addEvents([Event("mock_event", {})], (_e), {"preventDefault": true})}]
PASSED tests/utils/test_format.py::test_format_prop[prop15-{{"a": "red", "b": "blue"}}]
PASSED tests/utils/test_format.py::test_format_prop[prop16-{var}]
PASSED tests/utils/test_format.py::test_format_prop[prop17-{_}]
PASSED tests/utils/test_format.py::test_format_prop[prop18-{state.colors["a"]}]
PASSED tests/utils/test_format.py::test_format_prop[prop19-{{"a": val}}]
PASSED tests/utils/test_format.py::test_format_prop[prop20-{{"a": "val"}}]
PASSED tests/utils/test_format.py::test_format_prop[prop21-{{"a": state.colors["val"]}}]
PASSED tests/utils/test_format.py::test_format_prop[prop22-{{"h1": ({node, ...props}) => <Heading {...props} as={`h1`} />}}]
PASSED tests/utils/test_format.py::test_format_props[single_props0-key_value_props0-output0]
PASSED tests/utils/test_format.py::test_get_handler_parts[input0-output0]
PASSED tests/utils/test_format.py::test_format_event_handler[input0-test_state.do_something]
PASSED tests/utils/test_format.py::test_format_event_handler[input1-test_state.child_state.change_both]
PASSED tests/utils/test_format.py::test_format_event_handler[input2-test_state.child_state.grandchild_state.do_nothing]
PASSED tests/utils/test_format.py::test_format_event[input0-Event("mock_event", {})]
PASSED tests/utils/test_format.py::test_format_event_chain[input0-addEvents([Event("mock_event", {}),Event("mock_event", {})])]
PASSED tests/utils/test_format.py::test_format_event_chain[input1-addEvents([Event("mock_event", {}),Event("mock_event", {})])]
PASSED tests/utils/test_format.py::test_format_query_params[input0-output0]
PASSED tests/utils/test_format.py::test_format_query_params[input1-output1]
PASSED tests/utils/test_format.py::test_format_state[input0-output0]
PASSED tests/utils/test_format.py::test_format_state[input1-output1]
PASSED tests/utils/test_format.py::test_format_ref[input1-ref_input1]
PASSED tests/utils/test_format.py::test_format_ref[input 1-ref_input_1]
PASSED tests/utils/test_format.py::test_format_ref[input-1-ref_input_1]
PASSED tests/utils/test_format.py::test_format_ref[input_1-ref_input_1]
PASSED tests/utils/test_format.py::test_format_ref[a long test?1! name-ref_a_long_test_1_name]
PASSED tests/utils/test_format.py::test_format_array_ref[input0-refs_my_array]
PASSED tests/utils/test_format.py::test_format_array_ref[input1-refs_my_array[0]]
PASSED tests/utils/test_format.py::test_format_array_ref[input2-refs_my_array[1]]
PASSED tests/utils/test_format.py::test_format_breadcrumbs[/foo-output0]
PASSED tests/utils/test_format.py::test_format_breadcrumbs[/foo/bar-output1]
PASSED tests/utils/test_format.py::test_format_breadcrumbs[/foo/bar/baz-output2]
PASSED tests/utils/test_format.py::test_format_library_name[library@^0.1.2-library]
PASSED tests/utils/test_format.py::test_format_library_name[library-library]
PASSED tests/utils/test_format.py::test_format_library_name[@library@^0.1.2-@library]
PASSED tests/utils/test_format.py::test_format_library_name[@library-@library]
PASSED tests/utils/test_format.py::test_json_dumps[None-null]
PASSED tests/utils/test_format.py::test_json_dumps[True-true]
PASSED tests/utils/test_format.py::test_json_dumps[1-1]
PASSED tests/utils/test_format.py::test_json_dumps[1.0-1.0]
PASSED tests/utils/test_format.py::test_json_dumps[input4-[]]
PASSED tests/utils/test_format.py::test_json_dumps[input5-[1, 2, 3]]
PASSED tests/utils/test_format.py::test_json_dumps[input6-{}]
PASSED tests/utils/test_format.py::test_json_dumps[input7-{"k1": false, "k2": true}]
PASSED tests/utils/test_format.py::test_json_dumps[input8-["1 day, 0:00:01.000001", "1 day, 0:00:01.000002"]]
PASSED tests/utils/test_format.py::test_json_dumps[input9-{"key1": "1 day, 0:00:01.000001", "key2": "1 day, 0:00:01.000002"}]
PASSED tests/utils/test_hosting.py::test_get_existing_access_token_and_no_invitation_code
PASSED tests/utils/test_hosting.py::test_get_existing_access_token_and_invitation_code
PASSED tests/utils/test_hosting.py::test_no_existing_access_token
PASSED tests/utils/test_hosting.py::test_no_config_file
PASSED tests/utils/test_hosting.py::test_empty_config_file
PASSED tests/utils/test_hosting.py::test_invalid_json_config_file
PASSED tests/utils/test_hosting.py::test_validate_token_success
PASSED tests/utils/test_hosting.py::test_invalid_token_access_denied
PASSED tests/utils/test_hosting.py::test_unable_to_validate_token
PASSED tests/utils/test_hosting.py::test_delete_access_token_from_config
PASSED tests/utils/test_hosting.py::test_save_access_token_and_invitation_code_to_config
PASSED tests/utils/test_hosting.py::test_save_access_code_but_none_invitation_code_to_config
PASSED tests/utils/test_hosting.py::test_authenticated_token_success
PASSED tests/utils/test_hosting.py::test_no_authenticated_token
PASSED tests/utils/test_hosting.py::test_maybe_authenticated_token_is_invalid
PASSED tests/utils/test_hosting.py::test_prepare_deploy_not_authenticated
PASSED tests/utils/test_hosting.py::test_server_unable_to_prepare_deploy
PASSED tests/utils/test_hosting.py::test_prepare_deploy_success
PASSED tests/utils/test_hosting.py::test_deploy
PASSED tests/utils/test_hosting.py::test_validate_token_with_retries_failed
PASSED tests/utils/test_hosting.py::test_validate_token_with_retries_access_denied
PASSED tests/utils/test_hosting.py::test_validate_token_with_retries_success
PASSED tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response0-expected0]
PASSED tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response1-expected1]
PASSED tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response2-expected2]
PASSED tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_input_accepted
PASSED tests/utils/test_hosting.py::test_process_envs
PASSED tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs0-expected0]
PASSED tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs1-expected1]
PASSED tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs2-expected2]
PASSED tests/utils/test_hosting.py::test_requirements_txt_only_contains_reflex
PASSED tests/utils/test_hosting.py::test_requirements_txt_only_contains_other_packages
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var1-display_color_name-render_dict1]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var2-display_shade-render_dict2]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var3-display_primary_colors-render_dict3]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var4-display_color_with_shades-render_dict4]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var5-display_nested_color_with_shades-render_dict5]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var6-display_nested_color_with_shades_v2-render_dict6]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var7-display_color_tuple-render_dict7]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var8-display_colors_set-render_dict8]
FAILED tests/components/layout/test_foreach.py::test_foreach_render[state_var9-<lambda>-render_dict9]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args0-None]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args1-values1]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args2-values2]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args3-values3]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args4-values4]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args5-values5]
FAILED tests/test_reflex.py::test_deploy_non_interactive_success[optional_args6-values6]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses0-user_input_region0-user_input_envs0-i-want-this-site-None]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses1-user_input_region1-user_input_envs1-i-want-this-site-args_patch1]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses2-user_input_region2-user_input_envs2-suggested-key-None]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses3-user_input_region3-user_input_envs3-suggested-key-args_patch3]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses4-user_input_region4-user_input_envs4-i-want-this-site-None]
FAILED tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses5-user_input_region5-user_input_envs5-i-want-this-site-args_patch5]
======================== 22 failed, 295 passed in 2.09s ========================
