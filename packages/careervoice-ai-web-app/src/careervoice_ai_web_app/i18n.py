"""Internationalization support for CareerVoice AI."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from enum import StrEnum
from typing import Final

LANGUAGE_STATE_KEY = "app_language"


class AppLanguage(StrEnum):
    """Languages supported by the CareerVoice interface."""

    ENGLISH = "en"
    SIMPLIFIED_CHINESE = "zh-CN"


DEFAULT_LANGUAGE = AppLanguage.ENGLISH


LANGUAGE_LABELS: Final = {
    AppLanguage.ENGLISH: "ENG",
    AppLanguage.SIMPLIFIED_CHINESE: "简体中文",
}


TRANSLATIONS: Final = {
    AppLanguage.ENGLISH: {
        # General
        "app.title": "CareerVoice AI",
        "language.label": "Language",
        # Login
        "login.sign_in": "Sign in to continue",
        "login.access_limited": "Access is limited to approved users.",
        "login.email": "Email",
        "login.send_code": "Send login code",
        "login.enter_email": "Enter your email address.",
        "login.invalid_email": "Enter a valid email address.",
        "login.code_sent": (
            "If this email has access, a login code has been sent. "
            "Check your inbox and spam folder."
        ),
        "login.code": "Login code",
        "login.submit": "Sign in",
        "login.enter_code": "Enter the login code from your email.",
        "login.failed": (
            "We couldn't sign you in. Check the code and try again, "
            "or contact the person who gave you access."
        ),
        "login.unavailable": (
            "Sign-in is temporarily unavailable. Please try again later."
        ),
        "login.initialization_unavailable": (
            "Sign-in is temporarily unavailable. "
            "Please contact the application administrator."
        ),
        "login.did_not_receive": "Didn't receive a code?",
        "login.resend_in": (
            "You can request another code in {seconds} seconds."
        ),
        "login.resend": "Resend code",
        "login.wait_resend": (
            "Please wait {seconds} seconds before requesting another code."
        ),
        "login.resend_error": (
            "We couldn't request another login code. "
            "Please try using a different email."
        ),
        "login.resend_sent": (
            "If this email has access, a new login code has been sent."
        ),
        "login.use_different_email": "Use a different email",
        # Account
        "account.signed_in_as": "Signed in as {email}",
        "account.sign_out": "Sign out",
        # AI quota
        "quota.title": "AI assistance today",
        "quota.unavailable": (
            "AI usage information is temporarily unavailable."
        ),
        "quota.used": "{used} / {limit} AI units used",
        "quota.remaining": "{remaining} AI units remaining",
        "quota.unlimited": "Unlimited AI quota",
        "quota.used_unlimited": "{used} AI units used",
        "quota.today": "Today's usage",
        "quota.profile": "AI profile creation",
        "quota.voice": "Voice transcription",
        "quota.document": "Document recognition",
        "quota.ranking": "AI job ranking",
        "quota.run": "run",
        "quota.runs": "runs",
        "quota.unit": "unit",
        "quota.units": "units",
        "quota.shared": (
            "All AI features share the same "
            "{limit}-unit daily allowance."
        ),
        "quota.reset": "Resets daily at 00:00 UTC.",
        # Career profile input
        "profile.input.title": "Tell us about your career",
        "profile.input.intro": (
            "You can write about your career, upload an existing CV or "
            "career document, or describe your career by speaking."
        ),
        "profile.input.method_label": (
            "How would you like to provide your information?"
        ),
        "profile.input.write": "Write or paste",
        "profile.input.document": "Upload a document",
        "profile.input.voice": "Speak",
        "profile.text.label": "Career information and preferences",
        "profile.text.placeholder": (
            "Example: I am looking for a junior software developer "
            "or backend developer role in Adelaide. I prefer hybrid "
            "work and have experience with Python and SQL..."
        ),
        "profile.text.help": (
            "You can describe your experience, skills, preferred roles, "
            "locations, work arrangements, constraints, and career goals. "
            "Maximum {max_chars:,} characters."
        ),
        "profile.document.label": "Upload your CV or career document",
        "profile.document.help": (
            "Supported formats: TXT, PDF, and DOCX. "
            "Maximum file size: 5 MB."
        ),
        "profile.document.scan_label": (
            "Allow AI recognition for scanned PDFs"
        ),
        "profile.document.scan_help": (
            "If the uploaded PDF contains scanned images rather than "
            "selectable text, its pages may be sent to the configured "
            "AI service so the document text can be recognized."
        ),
        "profile.document.scan_available": (
            "Normal text-based PDFs are read locally. AI recognition is "
            "used only when a PDF has no readable text layer and you "
            "enable the option above."
        ),
        "profile.document.scan_unavailable": (
            "Text-based PDFs are supported. Scanned or image-only PDFs "
            "require AI document recognition, which is not currently "
            "available for this application."
        ),
        "profile.additional.label": (
            "Additional career preferences (optional)"
        ),
        "profile.additional.placeholder": (
            "Example: I am looking for junior backend roles in Adelaide. "
            "I prefer hybrid work and do not want senior positions."
        ),
        "profile.additional.help": (
            "A CV often describes your experience but not what you want "
            "next. Add any preferred roles, locations, work arrangements, "
            "constraints, or career goals that may be missing. "
            "Maximum {max_chars:,} characters."
        ),
        "profile.extractor.label": "Profile creation method",
        "profile.extractor.standard": "Standard extraction",
        "profile.extractor.ai": "AI-assisted extraction",
        "profile.extractor.help_available": (
            "Standard extraction is predictable and does not use an "
            "external AI service. AI-assisted extraction can understand "
            "more flexible descriptions."
        ),
        "profile.extractor.help_unavailable": (
            "Standard extraction is available. AI-assisted extraction "
            "is not currently available for this application."
        ),
        "profile.generate": "Generate career profile",
        "profile.generating": "Generating your career profile...",
        "profile.analyzing_text": (
            "Analyzing your career information and preparing the "
            "details for review."
        ),
        "profile.upload_required": (
            "Upload a TXT, PDF, or DOCX document before generating "
            "your career profile."
        ),
        "profile.reading_document": (
            "Reading your document and combining it with any "
            "additional career preferences."
        ),
        "profile.generated": "Career profile generated.",
        "profile.ready": (
            "Your career profile is ready. Review and correct the details "
            "before continuing."
        ),

        # Voice input
        "voice.intro": (
            "Record yourself describing your career background, skills, "
            "preferences, and what you are looking for next."
        ),
        "voice.unavailable": (
            "Voice transcription is not currently available because "
            "AI access is not configured for this application."
        ),
        "voice.record": "Record your career information",
        "voice.record_help": (
            "Your recording is sent to the configured speech-to-text "
            "service so it can be converted into editable text."
        ),
        "voice.review_hint": (
            "You will be able to review and edit the transcript before "
            "CareerVoice AI creates your career profile."
        ),
        "voice.transcribe": "Transcribe recording",
        "voice.transcribing": "Transcribing your recording...",
        "voice.transcribed": (
            "Recording transcribed. Review the text below before "
            "generating your career profile."
        ),
        "voice.review_title": "Review your transcript",
        "voice.review_intro": (
            "Correct anything the transcription misunderstood. "
            "The edited text, not the original recording, will be used "
            "to create your career profile."
        ),
        "voice.transcript_label": "Transcribed career information",
        "voice.transcript_help": (
            "Review names, technologies, locations, job titles, "
            "and other details before continuing. "
            "Maximum {max_chars:,} characters."
        ),
        "voice.extractor_help_available": (
            "Voice transcription already uses the configured "
            "speech-to-text service. Standard profile extraction "
            "does not make a second AI request; AI-assisted "
            "extraction does."
        ),
        "voice.extractor_help_unavailable": (
            "Standard extraction is available. AI-assisted extraction "
            "is not currently available."
        ),
        "voice.analyzing": (
            "Analyzing your reviewed transcript and preparing "
            "the details for review."
        ),
        # Career profile review
        "profile.review.title": "Review and edit your career profile",
        "profile.review.intro": (
            "Check the extracted details and correct anything that is "
            "missing or inaccurate. These details will be used to search "
            "and rank jobs."
        ),
        "profile.review.roles_section": "Roles, skills, and experience",
        "profile.review.target_roles": "Target roles",
        "profile.review.target_roles_help": "Enter one role per line.",
        "profile.review.skills": "Skills",
        "profile.review.skills_help": "Enter one skill per line.",
        "profile.review.experience_level": "Experience level",
        "profile.review.experience_placeholder": "Example: junior",
        "profile.review.locations": "Preferred locations",
        "profile.review.locations_help": "Enter one location per line.",
        "profile.review.preferences_section": (
            "Work preferences and constraints"
        ),
        "profile.review.work_types": "Preferred work types",
        "profile.review.work_type_placeholder": "Example: hybrid",
        "profile.review.work_types_help": (
            "Enter one work type per line."
        ),
        "profile.review.liked_areas": "Areas you like",
        "profile.review.liked_areas_help": "Enter one area per line.",
        "profile.review.disliked_areas": "Areas you want to avoid",
        "profile.review.disliked_areas_help": (
            "Enter one area per line."
        ),
        "profile.review.constraints": "Non-negotiable requirements",
        "profile.review.constraints_help": (
            "Enter one requirement per line."
        ),
        "profile.review.goals_section": "Goals and notes",
        "profile.review.goals": "Career goals",
        "profile.review.goals_help": "Enter one goal per line.",
        "profile.review.notes": "Notes and uncertainties",
        "profile.review.notes_help": "Enter one note per line.",
        "profile.review.confirm": "Save and confirm profile",
        "profile.review.saving": "Saving your reviewed profile...",
        "profile.review.view_data": "View profile data",
        "profile.review.download_data": "Download profile data",
        # Job search
        "job.search.title": "Configure your job search",
        "job.search.profile_confirmed": (
            "Your career profile has been saved and confirmed."
        ),
        "job.search.unavailable": (
            "Live job search is not currently available for this "
            "application. Your confirmed career profile will remain available."
        ),
        "job.search.intro": (
            "Review the roles and search settings below, then start the "
            "job search. Each role is searched separately."
        ),
        "job.search.roles": "Roles to search for",
        "job.search.roles_help": (
            "Enter up to {max_roles} roles, one role per line."
        ),
        "job.search.roles_caption": (
            "You can search up to {max_roles} roles at a time."
        ),
        "job.search.location": "Search location (optional)",
        "job.search.location_placeholder": "Example: Adelaide",
        "job.search.max_results": "Maximum listings per role",
        "job.search.max_results_help": (
            "This limit applies separately to each role before duplicate "
            "listings are removed. Maximum {max_results} listings per role."
        ),
        "job.search.provider": "Job listing provider",
        "job.search.provider_caption": (
            "The first web MVP currently searches Adzuna. "
            "Additional providers can be added later."
        ),
        "job.search.submit": "Search for jobs",
        "job.search.searching": "Searching for job listings...",
        "job.search.searching_detail": (
            "Searching each role using your confirmed location "
            "and result limit."
        ),
        "job.search.deduplicating": (
            "Combining the results and removing duplicate listings."
        ),
        "job.search.complete": (
            "Job search complete: {count} unique listings found."
        ),

        # Collected jobs
        "jobs.title": "Job listings found",
        "jobs.none": (
            "No job listings matched the current search. "
            "Try changing the roles, location, or result limit."
        ),
        "jobs.ready": "{count} unique job listings are ready.",
        "jobs.download": "Download job listings",
        "jobs.ranking_hint": (
            "Use the ranking section below to compare and explain these jobs."
        ),
        "jobs.column.title": "Title",
        "jobs.column.company": "Company",
        "jobs.column.location": "Location",
        "jobs.column.work_type": "Work type",
        "jobs.column.seniority": "Seniority",
        "jobs.not_provided": "Not provided",
        # Main application
        "app.tagline": (
            "Turn your career preferences into structured, explainable "
            "job recommendations."
        ),
        "session.invalid": (
            "Your session could not be verified. Please sign in again."
        ),

        # Runtime availability
        "runtime.warning": (
            "Some features are unavailable because the application "
            "setup is incomplete."
        ),
        "runtime.details": "Setup details",
        "runtime.feature.profile": "Career profile creation",
        "runtime.feature.jobs": "Job searching",
        "runtime.feature.recommendations": (
            "Job recommendation generation"
        ),
        "runtime.feature_unavailable": (
            "{feature} is currently unavailable."
        ),

        # Errors
        "error.job_collection": (
            "We couldn't complete the job search."
        ),
        "error.job_collection_hint": (
            "Check the search settings, internet connection, and "
            "job-provider configuration."
        ),
        "error.recommendation": (
            "We couldn't generate the job recommendations."
        ),
        "error.recommendation_hint": (
            "Try standard ranking, check the internet connection, "
            "or verify that AI access is available."
        ),
        "error.action_failed": (
            "We couldn't complete this action."
        ),
        "error.unexpected": (
            "An unexpected application error occurred. "
            "Please try again later."
        ),
        "error.technical_details": "Technical details",
        # Recommendation workflow
        "recommendation.workflow.title": (
            "Rank and explain your job matches"
        ),
        "recommendation.workflow.intro": (
            "Choose how the application should compare the collected "
            "jobs with your confirmed career profile."
        ),
        "recommendation.method.label": "Ranking method",
        "recommendation.method.standard": "Standard ranking",
        "recommendation.method.ai": "AI-assisted ranking",
        "recommendation.method.standard_short": "Standard",
        "recommendation.method.ai_short": "AI-assisted",
        "recommendation.method.unknown": "Unknown",
        "recommendation.method.help_available": (
            "Standard ranking is deterministic and does not use an "
            "external AI service. AI-assisted ranking can provide "
            "more flexible explanations."
        ),
        "recommendation.method.help_unavailable": (
            "Standard ranking is available. AI-assisted ranking is "
            "not currently available for this application."
        ),
        "recommendation.max_results": "Maximum recommendations",
        "recommendation.max_results_help": (
            "Show up to {max_results} ranked recommendations."
        ),
        "recommendation.hide_rejected": (
            "Hide jobs that conflict with non-negotiable requirements"
        ),
        "recommendation.generate": "Generate recommendations",
        "recommendation.ranking": (
            "Ranking and explaining the collected jobs..."
        ),
        "recommendation.comparing": (
            "Comparing each job with your roles, skills, preferences, "
            "and non-negotiable requirements."
        ),
        "recommendation.preparing": (
            "Preparing readable scores and explanations."
        ),
        "recommendation.ready_status": (
            "Recommendations ready: {count} jobs ranked."
        ),

        # Recommendation results
        "recommendation.results.title": "Recommended jobs",
        "recommendation.results.jobs_compared": "Jobs compared",
        "recommendation.results.shown": "Recommendations shown",
        "recommendation.results.method": "Ranking method",
        "recommendation.results.none": (
            "No recommendations matched the current settings. "
            "Try showing rejected jobs or increasing the "
            "recommendation limit."
        ),
        "recommendation.results.ready": (
            "{count} recommendations are ready."
        ),
        "recommendation.results.download": "Download recommendations",

        # Recommendation card
        "recommendation.card.untitled": "Untitled job",
        "recommendation.card.company_missing": "Company not provided",
        "recommendation.card.level": "Recommendation level",
        "recommendation.card.match_score": "Match score",
        "recommendation.card.rejected": (
            "This job conflicts with one or more "
            "non-negotiable requirements."
        ),
        "recommendation.card.matching_skills": "Matching skills",
        "recommendation.card.reasons": "Why this job may fit",
        "recommendation.card.missing_skills": "Missing skills",
        "recommendation.card.penalties": "Penalties and concerns",
        "recommendation.card.uncertainties": "Uncertainties",
        "recommendation.card.score_details": "View score details",
        "recommendation.card.match_details": "View matching details",

        # Recommendation levels
        "recommendation.level.default": "Recommendation",
        "recommendation.level.strong_match": "Strong Match",
        "recommendation.level.good_match": "Good Match",
        "recommendation.level.moderate_match": "Moderate Match",
        "recommendation.level.partial_match": "Partial Match",
        "recommendation.level.weak_match": "Weak Match",
        "recommendation.level.poor_match": "Poor Match",
    },
    AppLanguage.SIMPLIFIED_CHINESE: {
        # General
        "app.title": "CareerVoice AI",
        "language.label": "语言",
        # Login
        "login.sign_in": "登录以继续",
        "login.access_limited": "仅限已获批准的用户访问。",
        "login.email": "邮箱",
        "login.send_code": "发送登录验证码",
        "login.enter_email": "请输入邮箱地址。",
        "login.invalid_email": "请输入有效的邮箱地址。",
        "login.code_sent": (
            "如果此邮箱已获得访问权限，登录验证码已发送。"
            "请检查收件箱和垃圾邮件文件夹。"
        ),
        "login.code": "登录验证码",
        "login.submit": "登录",
        "login.enter_code": "请输入邮件中的登录验证码。",
        "login.failed": (
            "无法登录。请检查验证码后重试，"
            "或联系向你提供访问权限的人。"
        ),
        "login.unavailable": "登录暂时不可用，请稍后再试。",
        "login.initialization_unavailable": (
            "登录暂时不可用。请联系应用管理员。"
        ),
        "login.did_not_receive": "没有收到验证码？",
        "login.resend_in": "你可以在 {seconds} 秒后重新获取验证码。",
        "login.resend": "重发验证码",
        "login.wait_resend": (
            "请等待 {seconds} 秒后再重新获取验证码。"
        ),
        "login.resend_error": (
            "无法重新发送登录验证码。请尝试使用其他邮箱。"
        ),
        "login.resend_sent": (
            "如果此邮箱已获得访问权限，新的登录验证码已发送。"
        ),
        "login.use_different_email": "使用其他邮箱",
        # Account
        "account.signed_in_as": "已登录：{email}",
        "account.sign_out": "退出登录",
        # AI quota
        "quota.title": "今日 AI 辅助额度",
        "quota.unavailable": "暂时无法获取 AI 使用情况。",
        "quota.used": "已使用 {used} / {limit} 个 AI 单位",
        "quota.remaining": "剩余 {remaining} 个 AI 单位",
        "quota.unlimited": "无限 AI 配额",
        "quota.used_unlimited": "已使用 {used} 个 AI 单位",
        "quota.today": "今日使用情况",
        "quota.profile": "AI 职业画像生成",
        "quota.voice": "语音转文字",
        "quota.document": "文档识别",
        "quota.ranking": "AI 职位排序",
        "quota.run": "次",
        "quota.runs": "次",
        "quota.unit": "单位",
        "quota.units": "单位",
        "quota.shared": (
            "所有 AI 功能共享每日 {limit} 个单位的额度。"
        ),
        "quota.reset": "每日 00:00 UTC 重置。",
        # Career profile input
        "profile.input.title": "介绍你的职业情况",
        "profile.input.intro": (
            "你可以填写职业信息、上传现有简历或职业相关文档，"
            "也可以通过语音进行描述。"
        ),
        "profile.input.method_label": "你希望如何提供信息？",
        "profile.input.write": "填写或粘贴",
        "profile.input.document": "上传文档",
        "profile.input.voice": "语音输入",
        "profile.text.label": "职业信息与偏好",
        "profile.text.placeholder": (
            "例如：我正在阿德莱德寻找初级软件开发或后端开发岗位。"
            "我更偏好混合办公，并有 Python 和 SQL 经验……"
        ),
        "profile.text.help": (
            "你可以描述工作经历、技能、目标岗位、地区、工作方式、"
            "限制条件和职业目标。最多 {max_chars:,} 个字符。"
        ),
        "profile.document.label": "上传简历或职业相关文档",
        "profile.document.help": (
            "支持 TXT、PDF 和 DOCX 格式。文件大小上限为 5 MB。"
        ),
        "profile.document.scan_label": "允许 AI 识别扫描版 PDF",
        "profile.document.scan_help": (
            "如果上传的 PDF 由扫描图片组成而没有可选择的文字，"
            "页面可能会发送至已配置的 AI 服务以识别其中的文字。"
        ),
        "profile.document.scan_available": (
            "普通文本型 PDF 会在本地读取。只有当 PDF 没有可读取的"
            "文字层且你启用上方选项时，才会使用 AI 识别。"
        ),
        "profile.document.scan_unavailable": (
            "当前支持文本型 PDF。扫描版或仅包含图片的 PDF 需要 "
            "AI 文档识别，但此应用目前无法使用该功能。"
        ),
        "profile.additional.label": "补充职业偏好（可选）",
        "profile.additional.placeholder": (
            "例如：我希望在阿德莱德寻找初级后端岗位。"
            "我偏好混合办公，并且不考虑高级职位。"
        ),
        "profile.additional.help": (
            "简历通常主要描述你的经历，而不一定包含你下一步的求职偏好。"
            "你可以补充目标岗位、地区、工作方式、限制条件或职业目标。"
            "最多 {max_chars:,} 个字符。"
        ),
        "profile.extractor.label": "职业画像生成方式",
        "profile.extractor.standard": "标准提取",
        "profile.extractor.ai": "AI 辅助提取",
        "profile.extractor.help_available": (
            "标准提取结果较为稳定，并且不会调用外部 AI 服务。"
            "AI 辅助提取可以理解更灵活、更自然的描述。"
        ),
        "profile.extractor.help_unavailable": (
            "当前可以使用标准提取。此应用目前无法使用 AI 辅助提取。"
        ),
        "profile.generate": "生成职业画像",
        "profile.generating": "正在生成职业画像……",
        "profile.analyzing_text": (
            "正在分析你的职业信息并整理需要检查的内容。"
        ),
        "profile.upload_required": (
            "请先上传 TXT、PDF 或 DOCX 文档，再生成职业画像。"
        ),
        "profile.reading_document": (
            "正在读取文档，并与补充的职业偏好合并。"
        ),
        "profile.generated": "职业画像已生成。",
        "profile.ready": (
            "职业画像已准备好。请检查并修正信息后再继续。"
        ),

        # Voice input
        "voice.intro": (
            "请通过语音描述你的职业背景、技能、偏好，"
            "以及下一步希望寻找的机会。"
        ),
        "voice.unavailable": (
            "当前无法使用语音转文字，因为此应用尚未配置 AI 访问。"
        ),
        "voice.record": "录制职业信息",
        "voice.record_help": (
            "录音会发送至已配置的语音转文字服务，"
            "并转换为可以编辑的文字。"
        ),
        "voice.review_hint": (
            "在 CareerVoice AI 生成职业画像前，"
            "你可以先检查并编辑转写内容。"
        ),
        "voice.transcribe": "转写录音",
        "voice.transcribing": "正在转写录音……",
        "voice.transcribed": (
            "录音已转写。请先检查下方文字，再生成职业画像。"
        ),
        "voice.review_title": "检查并编辑转写内容",
        "voice.review_intro": (
            "请修正转写中可能识别错误的内容。生成职业画像时，"
            "将使用你编辑后的文字，而不是原始录音。"
        ),
        "voice.transcript_label": "转写后的职业信息",
        "voice.transcript_help": (
            "继续前请检查姓名、技术名称、地区、职位名称等信息。"
            "最多 {max_chars:,} 个字符。"
        ),
        "voice.extractor_help_available": (
            "语音转写已经使用了语音转文字服务。标准职业画像提取"
            "不会再次调用 AI；AI 辅助提取则会额外调用一次 AI。"
        ),
        "voice.extractor_help_unavailable": (
            "当前可以使用标准提取。AI 辅助提取目前不可用。"
        ),
        "voice.analyzing": (
            "正在分析你确认后的转写内容，并整理需要检查的信息。"
        ),
        # Career profile review
        "profile.review.title": "检查并编辑职业画像",
        "profile.review.intro": (
            "请检查提取的信息，并修正缺失或不准确的内容。"
            "这些信息将用于搜索职位并进行匹配排序。"
        ),
        "profile.review.roles_section": "岗位、技能与经验",
        "profile.review.target_roles": "目标岗位",
        "profile.review.target_roles_help": "每行填写一个岗位。",
        "profile.review.skills": "技能",
        "profile.review.skills_help": "每行填写一项技能。",
        "profile.review.experience_level": "经验水平",
        "profile.review.experience_placeholder": "例如：初级",
        "profile.review.locations": "偏好地区",
        "profile.review.locations_help": "每行填写一个地区。",
        "profile.review.preferences_section": "工作偏好与限制条件",
        "profile.review.work_types": "偏好的工作方式",
        "profile.review.work_type_placeholder": "例如：混合办公",
        "profile.review.work_types_help": "每行填写一种工作方式。",
        "profile.review.liked_areas": "感兴趣的领域",
        "profile.review.liked_areas_help": "每行填写一个领域。",
        "profile.review.disliked_areas": "希望避免的领域",
        "profile.review.disliked_areas_help": "每行填写一个领域。",
        "profile.review.constraints": "不可妥协的要求",
        "profile.review.constraints_help": "每行填写一项要求。",
        "profile.review.goals_section": "职业目标与备注",
        "profile.review.goals": "职业目标",
        "profile.review.goals_help": "每行填写一个目标。",
        "profile.review.notes": "备注与不确定信息",
        "profile.review.notes_help": "每行填写一条备注。",
        "profile.review.confirm": "保存并确认职业画像",
        "profile.review.saving": "正在保存确认后的职业画像……",
        "profile.review.view_data": "查看职业画像数据",
        "profile.review.download_data": "下载职业画像数据",
        # Job search
        "job.search.title": "配置职位搜索",
        "job.search.profile_confirmed": "职业画像已保存并确认。",
        "job.search.unavailable": (
            "当前无法使用实时职位搜索。已确认的职业画像仍会保留。"
        ),
        "job.search.intro": (
            "请检查下方的目标岗位和搜索设置，然后开始职位搜索。"
            "系统会分别搜索每个岗位。"
        ),
        "job.search.roles": "要搜索的岗位",
        "job.search.roles_help": (
            "最多输入 {max_roles} 个岗位，每行一个。"
        ),
        "job.search.roles_caption": (
            "每次最多可以搜索 {max_roles} 个岗位。"
        ),
        "job.search.location": "搜索地区（可选）",
        "job.search.location_placeholder": "例如：Adelaide",
        "job.search.max_results": "每个岗位最多职位数",
        "job.search.max_results_help": (
            "此限制会分别应用于每个岗位，然后再移除重复职位。"
            "每个岗位最多 {max_results} 条职位信息。"
        ),
        "job.search.provider": "职位信息来源",
        "job.search.provider_caption": (
            "当前 Web MVP 使用 Adzuna 搜索职位。"
            "未来可以增加其他职位来源。"
        ),
        "job.search.submit": "搜索职位",
        "job.search.searching": "正在搜索职位……",
        "job.search.searching_detail": (
            "正在根据已确认的地区和结果数量限制分别搜索每个岗位。"
        ),
        "job.search.deduplicating": (
            "正在合并搜索结果并移除重复职位。"
        ),
        "job.search.complete": (
            "职位搜索完成：找到 {count} 条去重后的职位信息。"
        ),

        # Collected jobs
        "jobs.title": "找到的职位",
        "jobs.none": (
            "当前搜索没有找到匹配的职位。"
            "请尝试修改岗位、地区或结果数量限制。"
        ),
        "jobs.ready": "已找到 {count} 条去重后的职位信息。",
        "jobs.download": "下载职位数据",
        "jobs.ranking_hint": (
            "使用下方的职位匹配功能比较这些职位并查看解释。"
        ),
        "jobs.column.title": "职位名称",
        "jobs.column.company": "公司",
        "jobs.column.location": "地区",
        "jobs.column.work_type": "工作方式",
        "jobs.column.seniority": "职级",
        "jobs.not_provided": "未提供",
        # Main application
        "app.tagline": (
            "将你的职业偏好转化为结构化、可解释的职位推荐。"
        ),
        "session.invalid": (
            "无法验证当前登录状态，请重新登录。"
        ),

        # Runtime availability
        "runtime.warning": (
            "由于应用配置尚未完整，部分功能当前无法使用。"
        ),
        "runtime.details": "配置详情",
        "runtime.feature.profile": "职业画像生成",
        "runtime.feature.jobs": "职位搜索",
        "runtime.feature.recommendations": "职位推荐生成",
        "runtime.feature_unavailable": (
            "{feature}当前无法使用。"
        ),

        # Errors
        "error.job_collection": (
            "无法完成职位搜索。"
        ),
        "error.job_collection_hint": (
            "请检查搜索设置、网络连接以及职位数据来源配置。"
        ),
        "error.recommendation": (
            "无法生成职位推荐。"
        ),
        "error.recommendation_hint": (
            "请尝试使用标准排序、检查网络连接，"
            "或确认 AI 功能当前可用。"
        ),
        "error.action_failed": (
            "无法完成当前操作。"
        ),
        "error.unexpected": (
            "应用发生了意外错误，请稍后再试。"
        ),
        "error.technical_details": "技术详情",
        # Recommendation workflow
        "recommendation.workflow.title": "职位匹配与解释",
        "recommendation.workflow.intro": (
            "选择系统如何将已找到的职位与你确认后的职业画像进行比较。"
        ),
        "recommendation.method.label": "排序方式",
        "recommendation.method.standard": "标准排序",
        "recommendation.method.ai": "AI 辅助排序",
        "recommendation.method.standard_short": "标准",
        "recommendation.method.ai_short": "AI 辅助",
        "recommendation.method.unknown": "未知",
        "recommendation.method.help_available": (
            "标准排序采用确定性的规则，不会调用外部 AI 服务。"
            "AI 辅助排序可以提供更灵活的解释。"
        ),
        "recommendation.method.help_unavailable": (
            "当前可以使用标准排序。此应用目前无法使用 AI 辅助排序。"
        ),
        "recommendation.max_results": "最多显示的推荐职位",
        "recommendation.max_results_help": (
            "最多显示 {max_results} 个排序后的推荐职位。"
        ),
        "recommendation.hide_rejected": (
            "隐藏违反不可妥协要求的职位"
        ),
        "recommendation.generate": "生成职位推荐",
        "recommendation.ranking": "正在排序并解释职位匹配……",
        "recommendation.comparing": (
            "正在根据你的目标岗位、技能、偏好和不可妥协要求"
            "比较每个职位。"
        ),
        "recommendation.preparing": (
            "正在整理易于阅读的分数和解释。"
        ),
        "recommendation.ready_status": (
            "职位推荐已准备好：已排序 {count} 个职位。"
        ),

        # Recommendation results
        "recommendation.results.title": "推荐职位",
        "recommendation.results.jobs_compared": "已比较职位",
        "recommendation.results.shown": "显示的推荐",
        "recommendation.results.method": "排序方式",
        "recommendation.results.none": (
            "当前设置下没有找到匹配的推荐职位。"
            "请尝试显示被限制条件排除的职位，或增加推荐数量。"
        ),
        "recommendation.results.ready": (
            "已生成 {count} 个职位推荐。"
        ),
        "recommendation.results.download": "下载职位推荐",

        # Recommendation card
        "recommendation.card.untitled": "未命名职位",
        "recommendation.card.company_missing": "未提供公司信息",
        "recommendation.card.level": "推荐等级",
        "recommendation.card.match_score": "匹配分数",
        "recommendation.card.rejected": (
            "该职位与一项或多项不可妥协要求冲突。"
        ),
        "recommendation.card.matching_skills": "匹配的技能",
        "recommendation.card.reasons": "为什么这个职位可能适合你",
        "recommendation.card.missing_skills": "缺少的技能",
        "recommendation.card.penalties": "扣分项与注意事项",
        "recommendation.card.uncertainties": "不确定信息",
        "recommendation.card.score_details": "查看评分详情",
        "recommendation.card.match_details": "查看匹配详情",

        # Recommendation levels
        "recommendation.level.default": "推荐",
        "recommendation.level.strong_match": "高度匹配",
        "recommendation.level.good_match": "良好匹配",
        "recommendation.level.moderate_match": "中度匹配",
        "recommendation.level.partial_match": "部分匹配",
        "recommendation.level.weak_match": "较弱匹配",
        "recommendation.level.poor_match": "较低匹配",
    },
}


def parse_app_language(
    value: object,
) -> AppLanguage | None:
    """Convert a stored value into a supported language."""
    if isinstance(value, AppLanguage):
        return value

    if isinstance(value, str):
        try:
            return AppLanguage(value)
        except ValueError:
            return None

    return None


def get_app_language(
    state: Mapping[str, object],
) -> AppLanguage:
    """Return the selected application language."""
    language = parse_app_language(
        state.get(LANGUAGE_STATE_KEY)
    )

    if language is None:
        return DEFAULT_LANGUAGE

    return language


def set_app_language(
    state: MutableMapping[str, object],
    language: AppLanguage,
) -> None:
    """Store the selected application language."""
    if not isinstance(language, AppLanguage):
        raise TypeError(
            "language must be an AppLanguage."
        )

    state[LANGUAGE_STATE_KEY] = language.value


def translate(
    language: AppLanguage,
    key: str,
    **values: object,
) -> str:
    """Return a translated user-facing string."""
    try:
        template = TRANSLATIONS[language][key]
    except KeyError as exc:
        raise KeyError(
            f"Missing translation for {language.value}: {key}"
        ) from exc

    return template.format(**values)