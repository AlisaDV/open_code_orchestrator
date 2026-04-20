from opencode_orchestrator.cli import build_parser


def test_cli_accepts_resume_without_objective() -> None:
    parser = build_parser()
    args = parser.parse_args(["--resume", "--approve-all"])

    assert args.resume is True
    assert args.approve_all is True
    assert args.objective is None


def test_cli_accepts_explicit_approval_mode() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "--approval-mode", "run"])

    assert args.objective == "task"
    assert args.approval_mode == "run"
