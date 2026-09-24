============================= test session starts ==============================
collecting ... collected 187 items / 1 error

tests/components/base/test_script.py::test_script_inline PASSED          [  0%]
tests/components/base/test_script.py::test_script_src PASSED             [  1%]
tests/components/base/test_script.py::test_script_neither PASSED         [  1%]
tests/components/base/test_script.py::test_script_event_handler FAILED   [  2%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var0-display_color-render_dict0] PASSED [  2%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var1-display_color_name-render_dict1] PASSED [  3%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var2-display_shade-render_dict2] PASSED [  3%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var3-display_primary_colors-render_dict3] PASSED [  4%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var4-display_color_with_shades-render_dict4] PASSED [  4%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var5-display_nested_color_with_shades-render_dict5] PASSED [  5%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var6-display_nested_color_with_shades_v2-render_dict6] PASSED [  5%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var7-display_color_tuple-render_dict7] PASSED [  6%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var8-display_colors_set-render_dict8] PASSED [  6%]
tests/components/layout/test_foreach.py::test_foreach_render[state_var9-<lambda>-render_dict9] PASSED [  7%]
tests/components/test_component.py::test_set_style_attrs PASSED          [  8%]
tests/components/test_component.py::test_custom_attrs PASSED             [  8%]
tests/components/test_component.py::test_create_component PASSED         [  9%]
tests/components/test_component.py::test_add_style PASSED                [  9%]
tests/components/test_component.py::test_get_imports PASSED              [ 10%]
tests/components/test_component.py::test_get_custom_code PASSED          [ 10%]
tests/components/test_component.py::test_get_props PASSED                [ 11%]
tests/components/test_component.py::test_valid_props[-0] PASSED          [ 11%]
tests/components/test_component.py::test_valid_props[test-1] PASSED      [ 12%]
tests/components/test_component.py::test_valid_props[hi--13] PASSED      [ 12%]
tests/components/test_component.py::test_invalid_prop_type[-bad_string] PASSED [ 13%]
tests/components/test_component.py::test_invalid_prop_type[13-1] PASSED  [ 13%]
tests/components/test_component.py::test_invalid_prop_type[None-1] PASSED [ 14%]
tests/components/test_component.py::test_invalid_prop_type[test-number3] PASSED [ 14%]
tests/components/test_component.py::test_var_props PASSED                [ 15%]
tests/components/test_component.py::test_get_event_triggers PASSED       [ 16%]
tests/components/test_component.py::test_component_event_trigger_arbitrary_args FAILED [ 16%]
tests/components/test_component.py::test_create_custom_component PASSED  [ 17%]
tests/components/test_component.py::test_custom_component_hash PASSED    [ 17%]
tests/components/test_component.py::test_custom_component_wrapper PASSED [ 18%]
tests/components/test_component.py::test_invalid_event_handler_args PASSED [ 18%]
tests/components/test_component.py::test_get_hooks_nested PASSED         [ 19%]
tests/components/test_component.py::test_get_hooks_nested2 PASSED        [ 19%]
tests/components/test_component.py::test_unsupported_child_components[component5] PASSED [ 20%]
tests/components/test_component.py::test_unsupported_child_components[component6] PASSED [ 20%]
tests/components/test_component.py::test_component_with_only_valid_children[component5] PASSED [ 21%]
tests/components/test_component.py::test_component_with_only_valid_children[component7] PASSED [ 21%]
tests/components/test_component.py::test_format_component[component0-<Text>\n  {`hi`}\n</Text>] PASSED [ 22%]
tests/components/test_component.py::test_format_component[component1-<Box>\n  <Heading size={`md`}>\n  {`test`}\n</Heading>\n</Box>] PASSED [ 22%]
tests/test_app.py::test_default_app PASSED                               [ 23%]
tests/test_app.py::test_multiple_states_error PASSED                     [ 24%]
tests/test_app.py::test_add_page_default_route PASSED                    [ 24%]
tests/test_app.py::test_add_page_set_route PASSED                        [ 25%]
tests/test_app.py::test_add_page_set_route_dynamic PASSED                [ 25%]
tests/test_app.py::test_add_page_set_route_nested PASSED                 [ 26%]
tests/test_app.py::test_initialize_with_admin_dashboard PASSED           [ 26%]
tests/test_app.py::test_initialize_with_custom_admin_dashboard PASSED    [ 27%]
tests/test_app.py::test_initialize_admin_dashboard_with_view_overrides PASSED [ 27%]
tests/test_app.py::test_initialize_with_state PASSED                     [ 28%]
tests/test_app.py::test_set_and_get_state PASSED                         [ 28%]
tests/test_app.py::test_dynamic_var_event PASSED                         [ 29%]
tests/test_app.py::test_list_mutation_detection__plain_list[append then __setitem__] PASSED [ 29%]
tests/test_app.py::test_list_mutation_detection__plain_list[delitem then append] PASSED [ 30%]
tests/test_app.py::test_list_mutation_detection__plain_list[extend, remove, pop, clear] PASSED [ 31%]
tests/test_app.py::test_list_mutation_detection__plain_list[nested list] PASSED [ 31%]
tests/test_app.py::test_list_mutation_detection__plain_list[list in dict] PASSED [ 32%]
tests/test_app.py::test_dict_mutation_detection__plain_list[update then __setitem__] PASSED [ 32%]
tests/test_app.py::test_dict_mutation_detection__plain_list[delitem then update] PASSED [ 33%]
tests/test_app.py::test_dict_mutation_detection__plain_list[add, remove, pop] PASSED [ 33%]
tests/test_app.py::test_dict_mutation_detection__plain_list[dict in list] PASSED [ 34%]
tests/test_app.py::test_dict_mutation_detection__plain_list[nested dict] PASSED [ 34%]
tests/test_app.py::test_upload_file[FileUploadState-delta0] PASSED       [ 35%]
tests/test_app.py::test_upload_file[ChildFileUploadState-delta1] PASSED  [ 35%]
tests/test_app.py::test_upload_file[GrandChildFileUploadState-delta2] PASSED [ 36%]
tests/test_app.py::test_upload_file_without_annotation[FileUploadState] PASSED [ 36%]
tests/test_app.py::test_upload_file_without_annotation[ChildFileUploadState] PASSED [ 37%]
tests/test_app.py::test_upload_file_without_annotation[GrandChildFileUploadState] PASSED [ 37%]
tests/test_app.py::test_dynamic_route_var_route_change_completed_on_load PASSED [ 38%]
tests/test_app.py::test_process_events PASSED                            [ 39%]
tests/test_app.py::test_overlay_component[None-default_overlay_component-None] PASSED [ 39%]
tests/test_app.py::test_overlay_component[None-None-None] PASSED         [ 40%]
tests/test_app.py::test_overlay_component[None-overlay_component2-Text] PASSED [ 40%]
tests/test_app.py::test_overlay_component[State-default_overlay_component-Fragment] PASSED [ 41%]
tests/test_app.py::test_overlay_component[State-None-None] PASSED        [ 41%]
tests/test_app.py::test_overlay_component[State-overlay_component5-Text] PASSED [ 42%]
tests/test_app.py::test_overlay_component[State-<lambda>-Text] PASSED    [ 42%]
tests/test_app.py::test_app_wrap_compile_theme PASSED                    [ 43%]
tests/test_app.py::test_app_wrap_priority PASSED                         [ 43%]
tests/test_config.py::test_requires_app_name PASSED                      [ 44%]
tests/test_config.py::test_set_app_name PASSED                           [ 44%]
tests/test_config.py::test_deprecated_params[db_config] PASSED           [ 45%]
tests/test_config.py::test_deprecated_params[admin_dash] PASSED          [ 45%]
tests/test_config.py::test_deprecated_params[env_path] PASSED            [ 46%]
tests/test_config.py::test_update_from_env[APP_NAME-my_test_app] PASSED  [ 47%]
tests/test_config.py::test_update_from_env[FRONTEND_PORT-3001] PASSED    [ 47%]
tests/test_config.py::test_update_from_env[FRONTEND_PATH-/test] PASSED   [ 48%]
tests/test_config.py::test_update_from_env[BACKEND_PORT-8001] PASSED     [ 48%]
tests/test_config.py::test_update_from_env[API_URL-https://mybackend.com:8000] PASSED [ 49%]
tests/test_config.py::test_update_from_env[DEPLOY_URL-https://myfrontend.com] PASSED [ 49%]
tests/test_config.py::test_update_from_env[BACKEND_HOST-127.0.0.1] PASSED [ 50%]
tests/test_config.py::test_update_from_env[DB_URL-postgresql://user:pass@localhost:5432/db] PASSED [ 50%]
tests/test_config.py::test_update_from_env[REDIS_URL-redis://localhost:6379] PASSED [ 51%]
tests/test_config.py::test_update_from_env[TIMEOUT-600] PASSED           [ 51%]
tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-False] PASSED [ 52%]
tests/test_config.py::test_update_from_env[TELEMETRY_ENABLED-True] PASSED [ 52%]
tests/test_config.py::test_event_namespace[kwargs0-/_event] PASSED       [ 53%]
tests/test_config.py::test_event_namespace[kwargs1-/api/_event] PASSED   [ 54%]
tests/test_config.py::test_event_namespace[kwargs2-/event] PASSED        [ 54%]
tests/test_config.py::test_event_namespace[kwargs3-/event] PASSED        [ 55%]
tests/test_config.py::test_event_namespace[kwargs4-/event] PASSED        [ 55%]
tests/test_config.py::test_event_namespace[kwargs5-/_event] PASSED       [ 56%]
tests/test_config.py::test_event_namespace[kwargs6-/_event] PASSED       [ 56%]
tests/test_config.py::test_event_namespace[kwargs7-/_event] PASSED       [ 57%]
tests/test_config.py::test_replace_defaults[config_kwargs0-env_vars0-set_persistent_vars0-exp_config_values0] PASSED [ 57%]
tests/test_config.py::test_replace_defaults[config_kwargs1-env_vars1-set_persistent_vars1-exp_config_values1] PASSED [ 58%]
tests/test_config.py::test_replace_defaults[config_kwargs2-env_vars2-set_persistent_vars2-exp_config_values2] PASSED [ 58%]
tests/test_config.py::test_replace_defaults[config_kwargs3-env_vars3-set_persistent_vars3-exp_config_values3] PASSED [ 59%]
tests/test_config.py::test_replace_defaults[config_kwargs4-env_vars4-set_persistent_vars4-exp_config_values4] PASSED [ 59%]
tests/test_event.py::test_create_event PASSED                            [ 60%]
tests/test_event.py::test_call_event_handler PASSED                      [ 60%]
tests/test_event.py::test_fix_events[1-20] PASSED                        [ 61%]
tests/test_event.py::test_fix_events[1-21] PASSED                        [ 62%]
tests/test_event.py::test_fix_events[arg12-arg22] PASSED                 [ 62%]
tests/test_event.py::test_event_redirect[input0-Event("_redirect", {path:`/path`,external:false})] PASSED [ 63%]
tests/test_event.py::test_event_redirect[input1-Event("_redirect", {path:`/path`,external:true})] PASSED [ 63%]
tests/test_event.py::test_event_redirect[input2-Event("_redirect", {path:`/path`,external:false})] PASSED [ 64%]
tests/test_event.py::test_event_redirect[input3-Event("_redirect", {path:path,external:false})] PASSED [ 64%]
tests/test_event.py::test_event_console_log PASSED                       [ 65%]
tests/test_event.py::test_event_window_alert PASSED                      [ 65%]
tests/test_event.py::test_set_focus PASSED                               [ 66%]
tests/test_event.py::test_set_value PASSED                               [ 66%]
tests/test_event.py::test_remove_cookie PASSED                           [ 67%]
tests/test_event.py::test_remove_cookie_with_options PASSED              [ 67%]
tests/test_event.py::test_clear_local_storage PASSED                     [ 68%]
tests/test_event.py::test_remove_local_storage PASSED                    [ 68%]
tests/test_event.py::test_event_actions FAILED                           [ 69%]
tests/test_event.py::test_event_actions_on_state FAILED                  [ 70%]
tests/test_reflex.py::test_login_success_existing_token PASSED           [ 70%]
tests/test_reflex.py::test_login_success_on_browser PASSED               [ 71%]
tests/test_reflex.py::test_login_fail PASSED                             [ 71%]
tests/test_reflex.py::test_deploy_required_args_missing[args0] PASSED    [ 72%]
tests/test_reflex.py::test_deploy_required_args_missing[args1] PASSED    [ 72%]
tests/test_reflex.py::test_deploy_required_args_missing[args2] PASSED    [ 73%]
tests/test_reflex.py::test_deploy_required_args_missing[args3] PASSED    [ 73%]
tests/test_reflex.py::test_deploy_required_args_missing[args4] PASSED    [ 74%]
tests/test_reflex.py::test_deploy_required_args_missing[args5] PASSED    [ 74%]
tests/test_reflex.py::test_deploy_non_interactive_prepare_failed PASSED  [ 75%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args0-None] FAILED [ 75%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args1-values1] FAILED [ 76%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args2-values2] FAILED [ 77%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args3-values3] FAILED [ 77%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args4-values4] FAILED [ 78%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args5-values5] FAILED [ 78%]
tests/test_reflex.py::test_deploy_non_interactive_success[optional_args6-values6] FAILED [ 79%]
tests/test_reflex.py::test_deploy_interactive_prepare_failed PASSED      [ 79%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses0-user_input_region0-user_input_envs0-i-want-this-site-None] FAILED [ 80%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses1-user_input_region1-user_input_envs1-i-want-this-site-args_patch1] FAILED [ 80%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses2-user_input_region2-user_input_envs2-suggested-key-None] FAILED [ 81%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses3-user_input_region3-user_input_envs3-suggested-key-args_patch3] FAILED [ 81%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses4-user_input_region4-user_input_envs4-i-want-this-site-None] FAILED [ 82%]
tests/test_reflex.py::test_deploy_interactive[fake-prefix-i-want-this-site-prepare_responses5-user_input_region5-user_input_envs5-i-want-this-site-args_patch5] FAILED [ 82%]
tests/utils/test_hosting.py::test_get_existing_access_token_and_no_invitation_code PASSED [ 83%]
tests/utils/test_hosting.py::test_get_existing_access_token_and_invitation_code PASSED [ 83%]
tests/utils/test_hosting.py::test_no_existing_access_token PASSED        [ 84%]
tests/utils/test_hosting.py::test_no_config_file PASSED                  [ 85%]
tests/utils/test_hosting.py::test_empty_config_file PASSED               [ 85%]
tests/utils/test_hosting.py::test_invalid_json_config_file PASSED        [ 86%]
tests/utils/test_hosting.py::test_validate_token_success PASSED          [ 86%]
tests/utils/test_hosting.py::test_invalid_token_access_denied PASSED     [ 87%]
tests/utils/test_hosting.py::test_unable_to_validate_token PASSED        [ 87%]
tests/utils/test_hosting.py::test_delete_access_token_from_config PASSED [ 88%]
tests/utils/test_hosting.py::test_save_access_token_and_invitation_code_to_config PASSED [ 88%]
tests/utils/test_hosting.py::test_save_access_code_but_none_invitation_code_to_config PASSED [ 89%]
tests/utils/test_hosting.py::test_authenticated_token_success PASSED     [ 89%]
tests/utils/test_hosting.py::test_no_authenticated_token PASSED          [ 90%]
tests/utils/test_hosting.py::test_maybe_authenticated_token_is_invalid PASSED [ 90%]
tests/utils/test_hosting.py::test_prepare_deploy_not_authenticated PASSED [ 91%]
tests/utils/test_hosting.py::test_server_unable_to_prepare_deploy PASSED [ 91%]
tests/utils/test_hosting.py::test_prepare_deploy_success PASSED          [ 92%]
tests/utils/test_hosting.py::test_deploy PASSED                          [ 93%]
tests/utils/test_hosting.py::test_validate_token_with_retries_failed PASSED [ 93%]
tests/utils/test_hosting.py::test_validate_token_with_retries_access_denied PASSED [ 94%]
tests/utils/test_hosting.py::test_validate_token_with_retries_success PASSED [ 94%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response0-expected0] PASSED [ 95%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response1-expected1] PASSED [ 95%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_accepts_defaults[prepare_response2-expected2] PASSED [ 96%]
tests/utils/test_hosting.py::test_interactive_get_deployment_key_user_input_accepted PASSED [ 96%]
tests/utils/test_hosting.py::test_process_envs PASSED                    [ 97%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs0-expected0] PASSED [ 97%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs1-expected1] PASSED [ 98%]
tests/utils/test_hosting.py::test_interactive_prompt_for_envs[inputs2-expected2] PASSED [ 98%]
tests/utils/test_hosting.py::test_requirements_txt_only_contains_reflex PASSED [ 99%]
tests/utils/test_hosting.py::test_requirements_txt_only_contains_other_packages PASSED [100%]

==================================== ERRORS ====================================
_________________ ERROR collecting tests/utils/test_format.py __________________
E   pydantic.error_wrappers.ValidationError: 1 validation error for EventChain
    event_actions
      value is not a valid set (type=type_error.set)
=================================== FAILURES ===================================
/home/reflex/tests/components/base/test_script.py:59: assert 'onReady={(_e) => addEvents([Event("ev_state.on_ready", {})], (_e), {})}' in ['onError={(_e) => addEvents([Event("ev_state.on_error", {})], (_e))}', 'onLoad={(_e) => addEvents([Event("ev_state.on_load", {})], (_e))}', 'onReady={(_e) => addEvents([Event("ev_state.on_ready", {})], (_e))}', 'src={`foo.js`}', 'strategy={`afterInteractive`}']
/home/reflex/tests/components/test_component.py:425: assert 'onFoo={(__e,...o,_charlie))}' == 'onFoo={(__e,...harlie), {})}'
/home/reflex/tests/test_event.py:274: AssertionError: assert {'stopPropagation'} == {'stopPropagation': True}
/home/reflex/tests/test_event.py:313: AssertionError: assert {'stopPropagation'} == {'stopPropagation': True}
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
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var0-display_color-render_dict0]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var1-display_color_name-render_dict1]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var2-display_shade-render_dict2]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var3-display_primary_colors-render_dict3]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var4-display_color_with_shades-render_dict4]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var5-display_nested_color_with_shades-render_dict5]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var6-display_nested_color_with_shades_v2-render_dict6]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var7-display_color_tuple-render_dict7]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var8-display_colors_set-render_dict8]
PASSED tests/components/layout/test_foreach.py::test_foreach_render[state_var9-<lambda>-render_dict9]
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
ERROR tests/utils/test_format.py - pydantic.error_wrappers.ValidationError: 1...
FAILED tests/components/base/test_script.py::test_script_event_handler - asse...
FAILED tests/components/test_component.py::test_component_event_trigger_arbitrary_args
FAILED tests/test_event.py::test_event_actions - AssertionError: assert {'sto...
FAILED tests/test_event.py::test_event_actions_on_state - AssertionError: ass...
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
=================== 17 failed, 170 passed, 1 error in 1.41s ====================
