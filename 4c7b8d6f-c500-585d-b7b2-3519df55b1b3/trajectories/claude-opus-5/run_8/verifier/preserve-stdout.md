
running 550 tests
test agecrypt::tests::test_age_x25519_round_trip_large ... ok
test agecrypt::tests::test_age_x25519_round_trip_small ... ok
test agecrypt::tests::test_parse_recipient ... ok
test backend::asdf::tests::test_debug ... ok
test backend::asset_matcher::tests::test_arch_mismatch_rejected ... ok
test backend::asset_matcher::tests::test_archive_preference ... ok
test backend::asset_matcher::tests::test_artifactbundle_penalty ... ok
test backend::asset_matcher::tests::test_asset_creation ... ok
test backend::asset_matcher::tests::test_asset_picker_functionality ... ok
test backend::asset_matcher::tests::test_asset_picker_functionality_mixed ... ok
test backend::asset_matcher::tests::test_asset_scoring ... ok
test backend::asset_matcher::tests::test_checksum_result_format ... ok
test backend::asset_matcher::tests::test_detect_checksum_algorithm ... ok
test backend::asset_matcher::tests::test_find_checksum ... ok
test backend::asset_matcher::tests::test_find_checksum_global ... ok
test backend::asset_matcher::tests::test_for_target_with_libc_qualifier ... ok
test backend::asset_matcher::tests::test_is_valid_hash ... ok
test backend::asset_matcher::tests::test_metadata_penalty ... ok
test backend::asset_matcher::tests::test_parse_checksum_content_returns_none_for_missing_file ... ok
test backend::asset_matcher::tests::test_parse_checksum_content_shasums_format ... ok
test backend::asset_matcher::tests::test_parse_checksum_content_single_file ... ok
test backend::asset_matcher::tests::test_parse_checksum_content_with_filename_suffix ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_darwin ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_intoto ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_none_available ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_selects_matching_platform ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_single_provenance ... ok
test backend::asset_matcher::tests::test_pick_best_provenance_windows ... ok
test backend::asset_matcher::tests::test_platform_detection_from_url ... ok
test backend::asset_matcher::tests::test_platform_string_conversion ... ok
test backend::asset_matcher::tests::test_vsix_vs_gz ... ok
test backend::asset_matcher::tests::test_windows_msvc_preference ... ok
test backend::asset_matcher::tests::test_zip_scoring ... ok
test backend::gem::tests::test_extract_minor_version ... ok
test backend::github::tests::test_find_asset_case_insensitive ... ok
test backend::github::tests::test_is_slsa_format_issue_api_error ... ok
test backend::github::tests::test_is_slsa_format_issue_invalid_format ... ok
test backend::github::tests::test_is_slsa_format_issue_no_attestations ... ok
test backend::github::tests::test_is_slsa_format_issue_no_certificate ... ok
test backend::github::tests::test_is_slsa_format_issue_no_dsse_envelope ... ok
test backend::github::tests::test_is_slsa_format_issue_real_verification_failure ... ok
test backend::github::tests::test_is_slsa_format_issue_signature_failure ... ok
test backend::github::tests::test_pattern_matching ... ok
test backend::github::tests::test_version_prefix_functionality ... ok
test backend::go::tests::parse_go_mod_info_with_versions ... ok
test backend::go::tests::parse_go_mod_info_without_versions ... ok
test backend::jq::tests::test_extract_array_field ... ok
test backend::jq::tests::test_extract_array_iterate ... ok
test backend::jq::tests::test_extract_auto_array_objects ... ok
test backend::jq::tests::test_extract_auto_array_strings ... ok
test backend::jq::tests::test_extract_auto_object_releases_field ... ok
test backend::jq::tests::test_extract_auto_object_versions_field ... ok
test backend::jq::tests::test_extract_auto_string ... ok
test backend::jq::tests::test_extract_deeply_nested ... ok
test backend::jq::tests::test_extract_empty_path ... ok
test backend::jq::tests::test_extract_filter_nested ... ok
test backend::jq::tests::test_extract_filter_no_match ... ok
test backend::jq::tests::test_extract_filter_simple ... ok
test backend::jq::tests::test_extract_filter_whole_object ... ok
test backend::jq::tests::test_extract_missing_field ... ok
test backend::jq::tests::test_extract_nested_array ... ok
test backend::jq::tests::test_extract_nested_field ... ok
test backend::jq::tests::test_extract_object_field_array ... ok
test backend::jq::tests::test_extract_root_array ... ok
test backend::jq::tests::test_extract_root_string ... ok
test backend::npm::tests::test_get_dependencies_default_package_manager ... ok
test backend::npm::tests::test_get_dependencies_for_npm_itself ... ok
test backend::platform_target::tests::test_from_current ... ok
test backend::platform_target::tests::test_platform_target_creation ... ok
test backend::platform_target::tests::test_platform_target_with_qualifier ... ok
test backend::s3::tests::test_s3_url_invalid_scheme ... ok
test backend::s3::tests::test_s3_url_missing_bucket ... ok
test backend::s3::tests::test_s3_url_parse_basic ... ok
test backend::s3::tests::test_s3_url_parse_deep_path ... ok
test backend::s3::tests::test_s3_url_parse_root_key ... ok
test backend::s3::tests::test_s3_url_parse_with_query_params ... ok
test backend::spm::tests::test_git_provider_from_ba ... ok
test backend::spm::tests::test_spm_repo_init_by_shorthand ... ok
test backend::spm::tests::test_spm_repo_init_by_url ... ok
test backend::spm::tests::test_spm_repo_init_name ... ok
test backend::static_helpers::tests::test_clean_binary_name ... ok
test backend::static_helpers::tests::test_keep_extensions ... ok
test backend::static_helpers::tests::test_keep_required_extensions ... ok
test backend::static_helpers::tests::test_list_available_platforms_with_key_flat_preserves_arch_underscore ... ok
test backend::static_helpers::tests::test_lookup_platform_key_bin ... ok
test backend::static_helpers::tests::test_lookup_platform_key_bin_path ... ok
test backend::static_helpers::tests::test_lookup_platform_key_bin_with_fallback ... ok
test backend::static_helpers::tests::test_lookup_platform_key_inline_format ... ok
test backend::static_helpers::tests::test_verify_artifact_fallback_to_generic ... ok
test backend::static_helpers::tests::test_verify_artifact_platform_specific ... ok
test backend::test_unalias_backend ... ok
test backend::tests::test_normalize_idiomatic_contents ... ok
test backend::version_list::tests::test_parse_empty_content ... ok
test backend::version_list::tests::test_parse_flutter_json_with_filter ... ok
test backend::version_list::tests::test_parse_flutter_with_version_expr ... ok
test backend::version_list::tests::test_parse_json_array_of_objects_with_tag_name ... ok
test backend::version_list::tests::test_parse_json_array_of_objects_with_version ... ok
test backend::version_list::tests::test_parse_json_array_of_strings ... ok
test backend::version_list::tests::test_parse_json_array_with_v_prefix ... ok
test backend::version_list::tests::test_parse_json_object_with_versions_array ... ok
test backend::version_list::tests::test_parse_json_path_with_invalid_json_falls_back_to_text ... ok
test backend::version_list::tests::test_parse_json_path_with_wrong_path_falls_back_to_text ... ok
test backend::version_list::tests::test_parse_line_separated_versions ... ok
test backend::version_list::tests::test_parse_line_separated_with_comments ... ok
test backend::version_list::tests::test_parse_removes_duplicates ... ok
test backend::version_list::tests::test_parse_single_version ... ok
test backend::version_list::tests::test_parse_single_version_with_v_prefix ... ok
test backend::version_list::tests::test_parse_whitespace_only ... ok
test backend::version_list::tests::test_parse_with_json_path_array_field ... ok
test backend::version_list::tests::test_parse_with_json_path_nested ... ok
test backend::version_list::tests::test_parse_with_json_path_object_array ... ok
test backend::version_list::tests::test_parse_with_regex ... ok
test backend::version_list::tests::test_parse_with_version_expr_filter_keys_with_regex ... ok
test backend::version_list::tests::test_parse_with_version_expr_json_keys ... ok
test backend::version_list::tests::test_parse_with_version_expr_split ... ok
test backend::vfox::test::test_verified_attestation_to_provenance_type ... ok
test backend::vfox::test::test_vfox_props ... ok
test cache::tests::test_cache ... ok
test cli::args::backend_arg::tests::test_backend_arg ... ok
test cli::args::backend_arg::tests::test_backend_arg_bug_fixes ... ok
test cli::args::backend_arg::tests::test_backend_arg_improved_error_messages ... ok
test cli::args::backend_arg::tests::test_backend_arg_pathname ... ok
test cli::args::backend_arg::tests::test_full_with_opts_appends_and_filters ... ok
test cli::args::backend_arg::tests::test_full_with_opts_preserves_existing_brackets ... ok
test cli::args::env_var_arg::tests::valid_values ... ok
test cli::args::tool_arg::tests::test_tool_arg ... ok
test cli::args::tool_arg::tests::test_tool_arg_parse_input ... ok
test cli::args::tool_arg::tests::test_tool_arg_with_version ... ok
test cli::args::tool_arg::tests::test_tool_arg_with_version_and_alias ... ok
test cli::lock::tests::test_is_not_unfiltered_lock_run_with_tool_filter ... ok
test cli::lock::tests::test_is_unfiltered_lock_run_without_tool_filter ... ok
test cli::lock::tests::test_prune_stale_entries_preserves_legacy_keyed_backend_match ... ok
test cli::lock::tests::test_prune_stale_entries_with_empty_tools_prunes_all_entries ... ok
test cli::lock::tests::test_prune_stale_entries_with_filter_keeps_existing_entries ... ok
test cli::plugins::install::tests::test_get_name_from_url ... ok
test cli::tests::test_subcommands_are_sorted ... ok
test cmd::tests::test_cmd ... ok
test config::config_file::config_root::tests::test_config_root ... ok
test config::config_file::config_root::tests::test_config_root_mise_dir ... ok
test config::config_file::idiomatic_version::package_json::tests::test_bun_as_package_manager ... ok
test config::config_file::idiomatic_version::package_json::tests::test_bun_logic ... ok
test config::config_file::idiomatic_version::package_json::tests::test_deno_dev_engines ... ok
test config::config_file::idiomatic_version::package_json::tests::test_dev_engines_overrides_package_manager_field ... ok
test config::config_file::idiomatic_version::package_json::tests::test_empty_dev_engines ... ok
test config::config_file::idiomatic_version::package_json::tests::test_engines_field_does_not_interfere ... ok
test config::config_file::idiomatic_version::package_json::tests::test_engines_field_ignored ... ok
test config::config_file::idiomatic_version::package_json::tests::test_missing_fields ... ok
test config::config_file::idiomatic_version::package_json::tests::test_package_manager_version_dev_engines ... ok
test config::config_file::idiomatic_version::package_json::tests::test_package_manager_version_field ... ok
test config::config_file::idiomatic_version::package_json::tests::test_package_manager_version_no_hash ... ok
test config::config_file::idiomatic_version::package_json::tests::test_parse_package_json ... ok
test config::config_file::idiomatic_version::package_json::tests::test_runtime_version ... ok
test config::config_file::idiomatic_version::package_json::tests::test_runtime_version_array_form ... ok
test config::config_file::idiomatic_version::package_json::tests::test_runtime_version_bun ... ok
test config::config_file::idiomatic_version::package_json::tests::test_runtime_version_missing_name ... ok
test config::config_file::idiomatic_version::package_json::tests::test_simplify_semver ... ok
test config::config_file::idiomatic_version::package_json::tests::test_simplify_semver_upper_bound ... ok
test config::config_file::idiomatic_version::package_json::tests::test_simplify_semver_wildcards ... ok
test config::config_file::idiomatic_version::tests::test_idiomatic_parse_error_propagation ... ok
test config::config_file::mise_toml::tests::test_env ... ok
test config::config_file::mise_toml::tests::test_env_arr ... ok
test config::config_file::mise_toml::tests::test_env_array_valid ... ok
test config::config_file::mise_toml::tests::test_env_entries ... ok
test config::config_file::mise_toml::tests::test_env_file ... ok
test config::config_file::mise_toml::tests::test_env_source_var_in_tool ... ok
test config::config_file::mise_toml::tests::test_env_var_in_tool ... FAILED
test config::config_file::mise_toml::tests::test_fixture ... FAILED
test config::config_file::mise_toml::tests::test_path_dirs ... ok
test config::config_file::mise_toml::tests::test_remove_alias ... ok
test config::config_file::mise_toml::tests::test_remove_plugin ... ok
test config::config_file::mise_toml::tests::test_replace_versions ... FAILED
test config::config_file::mise_toml::tests::test_set_alias ... ok
test config::config_file::mise_toml::tests::test_table_syntax_preserves_registry_defaults ... ok
test config::config_file::tests::test_detect_config_file_type ... ok
test config::config_file::tests::test_with_appended_extension ... ok
test config::config_file::toml::tests::test_deserialize_arr_map ... ok
test config::config_file::toml::tests::test_deserialize_arr_map_list ... ok
test config::config_file::toml::tests::test_deserialize_arr_mixed_list ... ok
test config::config_file::toml::tests::test_deserialize_arr_string ... ok
test config::config_file::toml::tests::test_deserialize_arr_string_list ... ok
test config::config_file::toml::tests::test_parse_arr ... ok
test config::config_file::toml::tests::test_parse_table ... ok
test config::env_directive::path::tests::test_env_path ... ok
test config::env_directive::venv::tests::test_venv_path ... ok
test config::miserc::tests::test_merge_settings ... ok
test config::miserc::tests::test_parse_miserc ... ok
test config::settings::tests::test_offline_default_is_false ... ok
test config::settings::tests::test_offline_implies_prefer_offline ... ok
test config::settings::tests::test_offline_setting_enables_offline ... ok
test config::settings::tests::test_prefer_offline_default_is_false ... ok
test config::settings::tests::test_prefer_offline_setting ... ok
test config::settings::tests::test_set_by_comma_duplicate_values ... ok
test config::settings::tests::test_set_by_comma_empty_elements ... ok
test config::settings::tests::test_set_by_comma_empty_string ... ok
test config::settings::tests::test_set_by_comma_multiple_values ... ok
test config::settings::tests::test_set_by_comma_single_value ... ok
test config::settings::tests::test_set_by_comma_trailing_comma ... ok
test config::settings::tests::test_set_by_comma_whitespace_only ... ok
test config::settings::tests::test_set_by_comma_with_whitespace ... ok
test config::settings::tests::test_settings_node_build_cmds ... ok
test config::settings::tests::test_settings_node_build_cmds_with_opts ... ok
test config::settings::tests::test_settings_toml_is_sorted ... ok
test config::tests::test_get_repo_url_ssh ... ok
test config::tests::test_load ... ok
test config::tests::test_load_all_config_files_skips_directories ... ok
test config::tests::test_load_task_file_supports_per_task_vars ... ok
test deps_graph::tests::test_cycle_detection ... ok
test deps_graph::tests::test_empty_graph ... ok
test deps_graph::tests::test_failure_blocks_dependents ... ok
test deps_graph::tests::test_linear_ordering ... ok
test deps_graph::tests::test_no_deps_all_ready ... ok
test deps_graph::tests::test_unknown_dep_error ... ok
test direnv::tests::test_add_path_to_old_and_new ... ok
test direnv::tests::test_dump ... ok
test direnv::tests::test_null_path ... ok
test direnv::tests::test_parse ... ok
test env::tests::test_apply_patches ... ok
test env::tests::test_token_overwrite ... ok
test env::tests::test_var_path ... ok
test env_diff::tests::test_diff ... ok
test env_diff::tests::test_from_bash_script ... ok
test env_diff::tests::test_invalid_escape_sequence ... ok
test env_diff::tests::test_reverse ... ok
test env_diff::tests::test_serialize ... ok
test file::tests::test_all_dirs_no_ceiling ... ok
test file::tests::test_all_dirs_with_ceiling ... ok
test file::tests::test_all_dirs_with_ceiling_at_start ... ok
test file::tests::test_all_dirs_with_multiple_ceilings ... ok
test file::tests::test_all_dirs_with_relative_path ... ok
test file::tests::test_dir_subdirs ... ok
test file::tests::test_display_path ... ok
test file::tests::test_find_up ... ok
test file::tests::test_find_up_2 ... ok
test file::tests::test_inspect_tar_contents_curdir_prefix ... ok
test file::tests::test_inspect_tar_contents_logic ... ok
test file::tests::test_replace_path ... ok
test file::tests::test_should_strip_components ... ok
test file::tests::test_tar_format_from_file_name ... ok
test file::tests::test_untar_single_file ... ok
test file::tests::test_untar_single_file_to_dir ... ok
test github::tests::test_parse_github_tokens ... ok
test github::tests::test_parse_github_tokens_empty ... ok
test github::tests::test_parse_github_tokens_empty_tokens ... ok
test github::tests::test_parse_github_tokens_missing_token_field ... ok
test hash::tests::test_hash_sha256 ... ok
test hash::tests::test_hash_to_str ... ok
test http::tests::test_documentation_examples ... ok
test http::tests::test_full_url_string_replacement ... ok
test http::tests::test_multiple_replacements_first_match_wins ... ok
test http::tests::test_no_replacements_configured ... ok
test http::tests::test_no_settings_configured ... ok
test http::tests::test_path_replacement_example ... ok
test http::tests::test_protocol_specific_replacement ... ok
test http::tests::test_regex_complex_patterns ... ok
test http::tests::test_regex_invalid_replacement_url ... ok
test http::tests::test_regex_replacement ... ok
test http::tests::test_regex_with_capture_groups ... ok
test http::tests::test_replacement_affects_full_url_not_just_hostname ... ok
test http::tests::test_simple_string_replacement ... ok
test lockfile::tests::test_array_format_required ... ok
test lockfile::tests::test_cleanup_unreferenced_conda_packages ... ok
test lockfile::tests::test_conda_packages_parsing ... ok
test lockfile::tests::test_conda_packages_serialization ... ok
test lockfile::tests::test_lockfile_path_for_config ... ok
test lockfile::tests::test_options_field_not_serialized_when_empty ... ok
test lockfile::tests::test_options_field_parsing_and_serialization ... ok
test lockfile::tests::test_options_field_serialized_when_present ... ok
test lockfile::tests::test_options_matching_in_get_locked_version ... ok
test lockfile::tests::test_platform_info_merge_prefers_sha256 ... ok
test lockfile::tests::test_provenance_fields_roundtrip ... ok
test lockfile::tests::test_provenance_legacy_provenance_url_compat ... ok
test lockfile::tests::test_provenance_merge_preserves_existing ... ok
test lockfile::tests::test_provenance_not_empty ... ok
test lockfile::tests::test_retain_tools_by_short_cleans_unreferenced_conda_packages ... ok
test lockfile::tests::test_retain_tools_by_short_or_backend_preserves_legacy_keyed_entries ... ok
test lockfile::tests::test_retain_tools_by_short_prunes_removed_tools ... ok
test lockfile::tests::test_save_uses_array_format ... ok
test lockfile::tests::test_stale_tool_shorts_identifies_removed_tools ... ok
test lockfile::tests::test_stale_tool_shorts_respects_backend_identifiers ... ok
test logger::tests::test_init ... ok
test parallel::tests::test_parallel ... ok
test path_env::tests::test_path_env ... ok
test path_env::tests::test_path_env_no_mise ... ok
test path_env::tests::test_path_env_with_colon ... ok
test platform::tests::test_common_platforms ... ok
test platform::tests::test_platform_helpers ... ok
test platform::tests::test_platform_multiple_parsing ... ok
test platform::tests::test_platform_parse_basic ... ok
test platform::tests::test_platform_parse_invalid ... ok
test platform::tests::test_platform_parse_with_compound_qualifier ... ok
test platform::tests::test_platform_parse_with_qualifier ... ok
test platform::tests::test_platform_to_key ... ok
test platform::tests::test_platform_validation ... ok
test plugins::core::ruby::tests::test_parse_gemfile ... ok
test plugins::core::ruby::tests::test_tag_to_version ... ok
test plugins::mise_plugin_toml::tests::test_exec_env ... ok
test plugins::mise_plugin_toml::tests::test_fixture ... ok
test plugins::script_manager::tests::test_get_script_path ... ok
test plugins::script_manager::tests::test_script_manager ... ok
test plugins::tests::test_plugin_source_parse_edge_cases ... ok
test plugins::tests::test_plugin_source_parse_git ... ok
test plugins::tests::test_plugin_source_parse_git_with_ref ... ok
test plugins::tests::test_plugin_source_parse_uppercase_zip_with_query ... ok
test plugins::tests::test_plugin_source_parse_zip ... ok
test prepare::prepare_deps::tests::test_cycle_detection ... ok
test prepare::prepare_deps::tests::test_diamond_deps ... ok
test prepare::prepare_deps::tests::test_empty_graph ... ok
test prepare::prepare_deps::tests::test_failure_blocks_dependents ... ok
test prepare::prepare_deps::tests::test_linear_ordering ... ok
test prepare::prepare_deps::tests::test_no_deps_all_ready ... ok
test prepare::prepare_deps::tests::test_unknown_dep_error ... ok
test redactions::tests::test_empty_patterns_filtered ... ok
test redactions::tests::test_empty_redactor ... ok
test redactions::tests::test_multiple_occurrences ... ok
test redactions::tests::test_multiple_patterns ... ok
test redactions::tests::test_overlapping_patterns ... ok
test redactions::tests::test_single_pattern ... ok
test redactions::tests::test_with_additional ... ok
test registry::tests::test_backend_env_override ... ok
test registry::tests::test_normalize_remote ... ok
test registry::tests::test_tool_disabled ... ok
test semver::tests::test_chunkify_version ... ok
test semver::tests::test_split_version_prefix ... ok
test shell::bash::tests::test_activate ... ok
test shell::bash::tests::test_deactivate ... ok
test shell::bash::tests::test_prepend_env ... ok
test shell::bash::tests::test_set_env ... ok
test shell::bash::tests::test_unset_env ... ok
test shell::elvish::tests::test_deactivate ... ok
test shell::elvish::tests::test_hook_init ... ok
test shell::elvish::tests::test_prepend_env ... ok
test shell::elvish::tests::test_set_env ... ok
test shell::elvish::tests::test_unset_env ... ok
test shell::fish::tests::test_activate ... ok
test shell::fish::tests::test_deactivate ... ok
test shell::fish::tests::test_move_prepend_env ... ok
test shell::fish::tests::test_prepend_env ... ok
test shell::fish::tests::test_set_env ... ok
test shell::fish::tests::test_unset_env ... ok
test shell::nushell::tests::test_deactivate ... ok
test shell::nushell::tests::test_hook_init ... ok
test shell::nushell::tests::test_prepend_env ... ok
test shell::nushell::tests::test_set_env ... ok
test shell::nushell::tests::test_unset_env ... ok
test shell::pwsh::tests::test_activate ... ok
test shell::pwsh::tests::test_deactivate ... ok
test shell::pwsh::tests::test_prepend_env ... ok
test shell::pwsh::tests::test_set_env ... ok
test shell::pwsh::tests::test_unset_env ... ok
test shell::xonsh::tests::test_hook_init ... ok
test shell::xonsh::tests::test_prepend_env ... ok
test shell::xonsh::tests::test_set_env ... ok
test shell::xonsh::tests::test_unset_env ... ok
test shell::xonsh::tests::test_xonsh_deactivate ... ok
test shell::xonsh::tests::test_xonsh_escape_sq ... ok
test shell::zsh::tests::test_activate ... FAILED
test shell::zsh::tests::test_deactivate ... FAILED
test shell::zsh::tests::test_prepend_env ... ok
test shell::zsh::tests::test_set_env ... ok
test shell::zsh::tests::test_unset_env ... ok
test shorthands::tests::test_get_shorthands ... ok
test shorthands::tests::test_get_shorthands_missing_file ... ok
test sysconfig::parser::tests::test_missing_assignment_error ... ok
test sysconfig::parser::tests::test_missing_header_error ... ok
test sysconfig::parser::tests::test_parse_concatenated_strings ... ok
test sysconfig::parser::tests::test_parse_escaped_quotes ... ok
test sysconfig::parser::tests::test_parse_integer_values ... ok
test sysconfig::parser::tests::test_parse_string ... ok
test sysconfig::parser::tests::test_parse_trailing_comma ... ok
test sysconfig::parser::tests::test_unexpected_character_error ... ok
test sysconfig::parser::tests::test_unexpected_comma ... ok
test sysconfig::parser::tests::test_unexpected_eof ... ok
test sysconfig::tests::remove_isysroot ... ok
test sysconfig::tests::test_replacements ... ok
test sysconfig::tests::update_real_prefix ... ok
test task::task_context_builder::tests::test_apply_env_results_basic ... ok
test task::task_context_builder::tests::test_apply_env_results_path_handling ... ok
test task::task_context_builder::tests::test_apply_env_results_removes_vars ... ok
test task::task_context_builder::tests::test_extract_task_env ... ok
test task::task_context_builder::tests::test_task_context_builder_new ... ok
test task::task_dep::tests::test_task_dep_deserialize_array ... ok
test task::task_dep::tests::test_task_dep_deserialize_object ... ok
test task::task_dep::tests::test_task_dep_deserialize_object_env_only ... ok
test task::task_dep::tests::test_task_dep_deserialize_string ... ok
test task::task_dep::tests::test_task_dep_display ... ok
test task::task_dep::tests::test_task_dep_from_str ... ok
test task::task_dep::tests::test_task_dep_only_env_vars_error ... ok
test task::task_dep::tests::test_task_dep_render_multiple_env ... ok
test task::task_dep::tests::test_task_dep_render_no_env ... ok
test task::task_dep::tests::test_task_dep_render_shell_style_env ... ok
test task::task_dep::tests::test_task_dep_serialize_with_env ... ok
test task::task_dep::tests::test_task_dep_single_token_with_equals ... ok
test task::task_file_providers::local_task::tests::test_get_local_path ... ok
test task::task_file_providers::local_task::tests::test_is_match ... ok
test task::task_file_providers::remote_task_git::tests::test_compare_https_get_cache_key ... ok
test task::task_file_providers::remote_task_git::tests::test_compare_ssh_get_cache_key ... ok
test task::task_file_providers::remote_task_git::tests::test_extract_https_url_information ... ok
test task::task_file_providers::remote_task_git::tests::test_extract_ssh_url_information ... ok
test task::task_file_providers::remote_task_git::tests::test_invalid_parse_https ... ok
test task::task_file_providers::remote_task_git::tests::test_invalid_parse_ssh ... ok
test task::task_file_providers::remote_task_git::tests::test_valid_parse_https ... ok
test task::task_file_providers::remote_task_git::tests::test_valid_parse_ssh ... ok
test task::task_file_providers::remote_task_http::tests::test_http_remote_task_get_local_path_with_cache ... ok
test task::task_file_providers::remote_task_http::tests::test_http_remote_task_get_local_path_without_cache ... ok
test task::task_file_providers::remote_task_http::tests::test_is_match ... ok
test task::task_file_providers::tests::test_get_providers ... ok
test task::task_file_providers::tests::test_git_file_match_git_remote_task_provider ... ok
test task::task_file_providers::tests::test_http_file_match_http_remote_task_provider ... ok
test task::task_file_providers::tests::test_local_file_match_local_provider ... ok
test task::task_load_context::tests::test_expand_colon_task_syntax ... ok
test task::task_load_context::tests::test_extract_path_hint ... ok
test task::task_load_context::tests::test_from_pattern_root_level_sets_load_all ... ok
test task::task_load_context::tests::test_from_pattern_with_path_does_not_set_load_all ... ok
test task::task_load_context::tests::test_load_all_context ... ok
test task::task_load_context::tests::test_should_load_subdir ... ok
test task::task_load_context::tests::test_should_load_subdir_multiple_hints ... ok
test task::task_scheduler::tests::test_scheduler_new ... ok
test task::task_scheduler::tests::test_scheduler_receiver_take ... ok
test task::task_scheduler::tests::test_spawn_context_clone ... ok
test task::task_script_parser::tests::test_task_nested_template ... ok
test task::task_script_parser::tests::test_task_parse_arg ... ok
test task::task_script_parser::tests::test_task_parse_arg_var ... ok
test task::task_script_parser::tests::test_task_parse_empty_help ... ok
test task::task_script_parser::tests::test_task_parse_flag ... ok
test task::task_script_parser::tests::test_task_parse_multi_use_arg ... ok
test task::task_script_parser::tests::test_task_parse_option ... ok
test task::task_script_parser::tests::test_task_parse_option_env ... ok
test task::task_script_parser::tests::test_task_parse_task_source_files ... ok
test task::task_script_parser::tests::test_task_usage_hashmap ... ok
test task::task_script_parser::tests::test_task_usage_multistring ... ok
test task::task_script_parser::tests::test_usage_arg_defaults_for_unprovided ... ok
test task::task_script_parser::tests::test_usage_arg_env ... ok
test task::task_script_parser::tests::test_usage_arg_renders ... ok
test task::task_script_parser::tests::test_usage_cmd_renders ... ok
test task::task_script_parser::tests::test_usage_combined ... ok
test task::task_script_parser::tests::test_usage_empty_and_spec_only ... ok
test task::task_script_parser::tests::test_usage_flag_defaults_for_unprovided ... ok
test task::task_script_parser::tests::test_usage_flag_renders ... ok
test task::task_script_parser::tests::test_usage_script_directives ... ok
test task::task_sources::tests::test_task_outputs_deserialize ... ok
test task::task_sources::tests::test_task_outputs_from_toml ... ok
test task::task_sources::tests::test_task_outputs_serialize ... ok
test task::task_template::tests::test_merge_template_depends_override ... ok
test task::task_template::tests::test_merge_template_description ... ok
test task::task_template::tests::test_merge_template_run_from_template ... ok
test task::task_template::tests::test_merge_template_run_override ... ok
test task::task_template::tests::test_merge_template_tools_deep_merge ... ok
test task::task_template::tests::test_merge_template_vars_deep_merge ... ok
test task::task_template::tests::test_merge_template_vars_override ... ok
test task::task_tool_installer::tests::test_task_tool_installer_new ... ok
test task::tests::test_circular_dependency_detection ... ok
test task::tests::test_extract_monorepo_path ... ok
test task::tests::test_file_path_absolute ... ok
test task::tests::test_file_path_none ... ok
test task::tests::test_file_path_raw_absolute ... ok
test task::tests::test_file_path_raw_none ... ok
test task::tests::test_file_path_raw_relative ... ok
test task::tests::test_file_path_raw_relative_no_config_root ... ok
test task::tests::test_file_path_relative ... ok
test task::tests::test_file_path_with_templating ... ok
test task::tests::test_from_path ... ok
test task::tests::test_from_path_env_file_with_spaces_around_equals ... ok
test task::tests::test_from_path_invalid_toml ... ok
test task::tests::test_from_path_toml_headers ... ok
test task::tests::test_get_matching_resolves_aliases ... ok
test task::tests::test_get_matching_resolves_monorepo_aliases ... ok
test task::tests::test_get_matching_wildcard_does_not_match_parent ... ok
test task::tests::test_hyphenated_and_numeric_tool_names ... ok
test task::tests::test_multi_line_tools_merge ... ok
test task::tests::test_name_from_path ... ok
test task::tests::test_name_from_path_invalid ... ok
test task::tests::test_no_false_positive_for_diamond_dependency ... ok
test task::tests::test_parses_all_fields ... ok
test task::tests::test_resolve_depends_post_uses_self_only ... ok
test task::tests::test_resolve_task_pattern ... ok
test task::tests::test_strip_extension ... ok
test task::tests::test_transitive_circular_dependency_detection ... ok
test tera::tests::test_absolute ... ok
test tera::tests::test_arch ... ok
test tera::tests::test_basename ... ok
test tera::tests::test_canonicalize ... ok
test tera::tests::test_choice ... ok
test tera::tests::test_config_root ... ok
test tera::tests::test_cwd ... ok
test tera::tests::test_dirname ... ok
test tera::tests::test_exists ... ok
test tera::tests::test_extname ... ok
test tera::tests::test_file_size ... ok
test tera::tests::test_file_stem ... ok
test tera::tests::test_haiku ... ok
test tera::tests::test_hash ... ok
test tera::tests::test_hash_file ... ok
test tera::tests::test_is_dir ... ok
test tera::tests::test_is_file ... ok
test tera::tests::test_join_path ... ok
test tera::tests::test_kebabcase ... ok
test tera::tests::test_last_modified ... ok
test tera::tests::test_lowercamelcase ... ok
test tera::tests::test_mise_bin ... ok
test tera::tests::test_mise_env ... ok
test tera::tests::test_mise_pid ... ok
test tera::tests::test_num_cpus ... ok
test tera::tests::test_os ... ok
test tera::tests::test_os_family ... ok
test tera::tests::test_quote ... ok
test tera::tests::test_read_file ... ok
test tera::tests::test_semver_matching ... ok
test tera::tests::test_shoutykebabcase ... ok
test tera::tests::test_shoutysnakecase ... ok
test tera::tests::test_snakecase ... ok
test tera::tests::test_uppercamelcase ... ok
test tera::tests::test_xdg_cache_home ... ok
test tera::tests::test_xdg_config_home ... ok
test tera::tests::test_xdg_data_home ... ok
test tera::tests::test_xdg_state_home ... ok
test toolset::env_cache::tests::test_cache_key_computation ... ok
test toolset::env_cache::tests::test_encryption_roundtrip ... ok
test toolset::env_cache::tests::test_generate_encryption_key ... ok
test toolset::install_state::tests::test_manifest_backward_compat_bracketed_full ... ok
test toolset::install_state::tests::test_manifest_roundtrip ... ok
test toolset::install_state::tests::test_manifest_with_opts_roundtrip ... ok
test toolset::install_state::tests::test_normalize_version_for_sort ... ok
test toolset::install_state::tests::test_version_sorting_with_v_prefix ... ok
test toolset::outdated_info::tests::test_check_semver_bump ... ok
test toolset::outdated_info::tests::test_is_outdated_version ... ok
test toolset::tests::test_sort_by_overrides ... ok
test toolset::tool_deps::tests::test_empty_deps ... ok
test toolset::tool_request::tests::test_version_sub ... ok
test toolset::tool_request::tests::test_version_sub_underflow ... ok
test toolset::tool_request_set::tests::test_load_runtime_env_ignores_non_mise_vars ... ok
test toolset::tool_request_set::tests::test_load_runtime_env_with_valid_utf8 ... ok
test toolset::tool_source::tests::test_tool_source_as_json ... ok
test toolset::tool_source::tests::test_tool_source_display ... ok
test toolset::tool_version_list::tests::test_tool_version_list ... ok
test toolset::tool_version_list::tests::test_tool_version_list_failure ... ok
test toolset::tool_version_options::tests::test_contains_key_with_nested_options ... ok
test toolset::tool_version_options::tests::test_direct_and_nested_options ... ok
test toolset::tool_version_options::tests::test_generic_nested_options ... ok
test toolset::tool_version_options::tests::test_indexmap_preserves_order ... ok
test toolset::tool_version_options::tests::test_merge_functionality ... ok
test toolset::tool_version_options::tests::test_nested_option_with_os_arch_dash ... ok
test toolset::tool_version_options::tests::test_non_existent_nested_paths ... ok
test toolset::tool_version_options::tests::test_parse_tool_options ... ok
test toolset::tool_version_options::tests::test_parse_tool_options_integer_strip_components ... ok
test toolset::tool_version_options::tests::test_parse_tool_options_mixed_braces_and_simple ... ok
test toolset::tool_version_options::tests::test_parse_tool_options_with_nested_braces ... ok
test ui::multi_progress_report::tests::test_multi_progress_report ... ok
test ui::progress_report::tests::test_progress_report ... ok
test ui::progress_report::tests::test_progress_report_quiet ... ok
test ui::progress_report::tests::test_progress_report_verbose ... ok

failures:

---- config::config_file::mise_toml::tests::test_env_var_in_tool stdout ----
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Snapshot Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Snapshot file: src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__env_var_in_tool.snap
Snapshot: env_var_in_tool
Source: src/config/config_file/mise_toml.rs:2028
────────────────────────────────────────────────────────────────────────────────
Expression: replace_path(&format!("{:#?}", cf.to_tool_request_set().unwrap().tools))
────────────────────────────────────────────────────────────────────────────────
-old snapshot
+new results
────────────┬───────────────────────────────────────────────────────────────────
    4     4 │             backend: BackendArg(terraform),
    5     5 │             version: "1.0.0",
    6     6 │             options: ToolVersionOptions {
    7     7 │                 os: None,
    8       │-                depends: None,
    9     8 │                 install_env: {},
   10     9 │                 opts: {},
   11    10 │             },
   12    11 │             source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   19    18 │             backend: BackendArg(jq),
   20    19 │             prefix: "1.6",
   21    20 │             options: ToolVersionOptions {
   22    21 │                 os: None,
   23       │-                depends: None,
   24    22 │                 install_env: {},
   25    23 │                 opts: {},
   26    24 │             },
   27    25 │             source: MiseToml(
────────────┴───────────────────────────────────────────────────────────────────
Stopped on the first failure. Run `cargo insta test` to run all snapshots.

thread 'config::config_file::mise_toml::tests::test_env_var_in_tool' panicked at /usr/local/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/insta-1.46.3/src/runtime.rs:719:13:
snapshot assertion for 'env_var_in_tool' failed in line 2028
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

---- config::config_file::mise_toml::tests::test_fixture stdout ----
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Snapshot Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Snapshot file: src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__fixture-3.snap
Snapshot: fixture-3
Source: src/config/config_file/mise_toml.rs:1973
────────────────────────────────────────────────────────────────────────────────
Expression: replace_path(&format!("{:#?}", cf.to_tool_request_set().unwrap()))
────────────────────────────────────────────────────────────────────────────────
-old snapshot
+new results
────────────┬───────────────────────────────────────────────────────────────────
    5     5 │                 backend: BackendArg(terraform),
    6     6 │                 version: "1.0.0",
    7     7 │                 options: ToolVersionOptions {
    8     8 │                     os: None,
    9       │-                    depends: None,
   10     9 │                     install_env: {},
   11    10 │                     opts: {},
   12    11 │                 },
   13    12 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   20    19 │                 backend: BackendArg(node),
   21    20 │                 version: "18",
   22    21 │                 options: ToolVersionOptions {
   23    22 │                     os: None,
   24       │-                    depends: None,
   25    23 │                     install_env: {},
   26    24 │                     opts: {},
   27    25 │                 },
   28    26 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   33    31 │                 backend: BackendArg(node),
   34    32 │                 prefix: "20",
   35    33 │                 options: ToolVersionOptions {
   36    34 │                     os: None,
   37       │-                    depends: None,
   38    35 │                     install_env: {},
   39    36 │                     opts: {},
   40    37 │                 },
   41    38 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   47    44 │                 ref_: "master",
   48    45 │                 ref_type: "ref",
   49    46 │                 options: ToolVersionOptions {
   50    47 │                     os: None,
   51       │-                    depends: None,
   52    48 │                     install_env: {},
   53    49 │                     opts: {},
   54    50 │                 },
   55    51 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   60    56 │                 backend: BackendArg(node),
   61    57 │                 path: "~/.nodes/18",
   62    58 │                 options: ToolVersionOptions {
   63    59 │                     os: None,
   64       │-                    depends: None,
   65    60 │                     install_env: {},
   66    61 │                     opts: {},
   67    62 │                 },
   68    63 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   75    70 │                 backend: BackendArg(jq),
   76    71 │                 prefix: "1.6",
   77    72 │                 options: ToolVersionOptions {
   78    73 │                     os: None,
   79       │-                    depends: None,
   80    74 │                     install_env: {},
   81    75 │                     opts: {},
   82    76 │                 },
   83    77 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   90    84 │                 backend: BackendArg(shellcheck),
   91    85 │                 version: "0.9.0",
   92    86 │                 options: ToolVersionOptions {
   93    87 │                     os: None,
   94       │-                    depends: None,
   95    88 │                     install_env: {},
   96    89 │                     opts: {},
   97    90 │                 },
   98    91 │                 source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
  105    98 │                 backend: BackendArg(python),
  106    99 │                 version: "3.10.0",
  107   100 │                 options: ToolVersionOptions {
  108   101 │                     os: None,
  109       │-                    depends: None,
  110   102 │                     install_env: {},
  111   103 │                     opts: {
  112   104 │                         "venv": String(
  113   105 │                             ".venv",
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
  122   114 │                 backend: BackendArg(python),
  123   115 │                 version: "3.9.0",
  124   116 │                 options: ToolVersionOptions {
  125   117 │                     os: None,
  126       │-                    depends: None,
  127   118 │                     install_env: {},
  128   119 │                     opts: {},
  129   120 │                 },
  130   121 │                 source: MiseToml(
────────────┴───────────────────────────────────────────────────────────────────
Stopped on the first failure. Run `cargo insta test` to run all snapshots.

thread 'config::config_file::mise_toml::tests::test_fixture' panicked at /usr/local/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/insta-1.46.3/src/runtime.rs:719:13:
snapshot assertion for 'fixture-3' failed in line 1973

---- config::config_file::mise_toml::tests::test_replace_versions stdout ----
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Snapshot Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Snapshot file: src/config/config_file/snapshots/mise__config__config_file__mise_toml__tests__replace_versions.snap
Snapshot: replace_versions
Source: src/config/config_file/mise_toml.rs:2262
────────────────────────────────────────────────────────────────────────────────
Expression: cf.to_toolset().unwrap()
────────────────────────────────────────────────────────────────────────────────
-old snapshot
+new results
────────────┬───────────────────────────────────────────────────────────────────
    8     8 │                     backend: BackendArg(node),
    9     9 │                     version: "16.0.1",
   10    10 │                     options: ToolVersionOptions {
   11    11 │                         os: None,
   12       │-                        depends: None,
   13    12 │                         install_env: {},
   14    13 │                         opts: {},
   15    14 │                     },
   16    15 │                     source: MiseToml(
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   21    20 │                     backend: BackendArg(node),
   22    21 │                     version: "18.0.1",
   23    22 │                     options: ToolVersionOptions {
   24    23 │                         os: None,
   25       │-                        depends: None,
   26    24 │                         install_env: {},
   27    25 │                         opts: {},
   28    26 │                     },
   29    27 │                     source: MiseToml(
────────────┴───────────────────────────────────────────────────────────────────
Stopped on the first failure. Run `cargo insta test` to run all snapshots.

thread 'config::config_file::mise_toml::tests::test_replace_versions' panicked at /usr/local/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/insta-1.46.3/src/runtime.rs:719:13:
snapshot assertion for 'replace_versions' failed in line 2262

---- shell::zsh::tests::test_activate stdout ----
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Snapshot Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Snapshot file: src/shell/snapshots/mise__shell__zsh__tests__activate.snap
Snapshot: activate
Source: src/shell/zsh.rs:172
────────────────────────────────────────────────────────────────────────────────
Expression: zsh.activate(opts)
────────────────────────────────────────────────────────────────────────────────
-old snapshot
+new results
────────────┬───────────────────────────────────────────────────────────────────
    2     2 │ if [ -z "${__MISE_ORIG_PATH:-}" ]; then
    3     3 │   export __MISE_ORIG_PATH="$PATH"
    4     4 │ fi
    5     5 │ export __MISE_ZSH_PRECMD_RUN=0
    6       │-export __MISE_ZSH_CHPWD_RAN=0
    7     6 │ 
    8     7 │ mise() {
    9     8 │   local command
   10     9 │   command="${1:-}"
┈┈┈┈┈┈┈┈┈┈┈┈┼┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   25    24 │   esac
   26    25 │   command /some/dir/mise "$command" "$@"
   27    26 │ }
   28    27 │ 
   29       │-autoload -Uz add-zsh-hook
   30    28 │ _mise_hook() {
   31    29 │   eval "$(/some/dir/mise hook-env --status -s zsh)";
   32    30 │ }
   33    31 │ _mise_hook_precmd() {
   34       │-  if [[ "${__MISE_ZSH_CHPWD_RAN:-0}" == "1" ]]; then
   35       │-    export __MISE_ZSH_CHPWD_RAN=0
   36       │-    return
   37       │-  fi
   38    32 │   eval "$(/some/dir/mise hook-env --status -s zsh --reason precmd)";
   39    33 │ }
   40    34 │ _mise_hook_chpwd() {
   41       │-  export __MISE_ZSH_CHPWD_RAN=1
   42    35 │   eval "$(/some/dir/mise hook-env --status -s zsh --reason chpwd)";
   43    36 │ }
         37 │+autoload -Uz add-zsh-hook
   44    38 │ add-zsh-hook precmd _mise_hook_precmd
   45    39 │ add-zsh-hook chpwd _mise_hook_chpwd
   46    40 │ 
   47    41 │ _mise_hook
────────────┴───────────────────────────────────────────────────────────────────
Stopped on the first failure. Run `cargo insta test` to run all snapshots.

thread 'shell::zsh::tests::test_activate' panicked at /usr/local/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/insta-1.46.3/src/runtime.rs:719:13:
snapshot assertion for 'activate' failed in line 172

---- shell::zsh::tests::test_deactivate stdout ----
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Snapshot Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Snapshot file: src/shell/snapshots/mise__shell__zsh__tests__deactivate.snap
Snapshot: deactivate
Source: src/shell/zsh.rs:194
────────────────────────────────────────────────────────────────────────────────
Expression: replace_path(&deactivate)
────────────────────────────────────────────────────────────────────────────────
-old snapshot
+new results
────────────┬───────────────────────────────────────────────────────────────────
    1     1 │ autoload -Uz add-zsh-hook
    2       │-add-zsh-hook -d precmd _mise_hook_precmd 2>/dev/null
    3       │-add-zsh-hook -d chpwd _mise_hook_chpwd 2>/dev/null
          2 │+add-zsh-hook -d precmd _mise_hook_precmd
          3 │+add-zsh-hook -d chpwd _mise_hook_chpwd
    4     4 │ (( $+functions[_mise_hook_precmd] )) && unset -f _mise_hook_precmd
    5     5 │ (( $+functions[_mise_hook_chpwd] )) && unset -f _mise_hook_chpwd
    6     6 │ (( $+functions[_mise_hook] )) && unset -f _mise_hook
    7     7 │ (( $+functions[mise] )) && unset -f mise
    8     8 │ unset MISE_SHELL
    9     9 │ unset __MISE_DIFF
   10    10 │ unset __MISE_SESSION
   11       │-unset __MISE_ZSH_PRECMD_RUN
   12       │-unset __MISE_ZSH_CHPWD_RAN
         11 │+unset __MISE_ZSH_PRECMD_RUN
────────────┴───────────────────────────────────────────────────────────────────
Stopped on the first failure. Run `cargo insta test` to run all snapshots.

thread 'shell::zsh::tests::test_deactivate' panicked at /usr/local/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/insta-1.46.3/src/runtime.rs:719:13:
snapshot assertion for 'deactivate' failed in line 194


failures:
    config::config_file::mise_toml::tests::test_env_var_in_tool
    config::config_file::mise_toml::tests::test_fixture
    config::config_file::mise_toml::tests::test_replace_versions
    shell::zsh::tests::test_activate
    shell::zsh::tests::test_deactivate

test result: FAILED. 545 passed; 5 failed; 0 ignored; 0 measured; 0 filtered out; finished in 3.90s

    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.49s
     Running unittests src/main.rs (target/debug/deps/mise-2ba9e4ba24544a8d)
foo
foo             message
foo             message                                                        ✔
foo             message                                                        ✔
error: test failed, to rerun pass `--bin mise`
