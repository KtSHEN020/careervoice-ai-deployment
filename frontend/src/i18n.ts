export type AppLanguage = 'en' | 'zh-CN'

const LANGUAGE_STORAGE_KEY = 'careervoice-language'

export const UI_TEXT = {
  en: {
    language: {
      select: 'Select language',
    },

    sidebar: {
      show: 'Show sidebar',
      hide: 'Hide sidebar',
      navigation: 'Workflow',
      profile: 'Profile',
      jobs: 'Jobs',
      matches: 'Matches',
      account: 'Account',
    },

    navigation: {
      backToProfile: '← Back to Profile',
      nextToJobs: 'Next: Jobs →',
      backToJobs: '← Back to Jobs',
      nextToMatches: 'Next: Matches →',
    },

    app: {
      signOut: 'Sign out',
      signingOut: 'Signing out…',
      signOutError: 'Sign out failed. Please try again.',
      profileExtracted: 'Profile extracted',
      readyForReview: 'Ready for review',
      targetRoles: 'target role(s)',
      skillsIdentified: 'skill(s) identified.',
      productSummary:
      'Build a profile, find jobs, and compare personalized matches.',
    },

    auth: {
      checking: 'Checking your session…',
      privateTesting: 'Private testing',
      signInTitle: 'Sign in to CareerVoice',
      approvedEmail:
        'Enter your approved email address to receive a verification code.',
      email: 'Email address',
      sendCode: 'Send verification code',
      sending: 'Sending…',

      verification: 'Email verification',
      enterCode: 'Enter your verification code',
      codeSentTo: 'We sent a verification code to',
      code: 'Verification code',
      codeSent:
        'A verification code has been sent to your email.',
      verify: 'Verify code',
      verifying: 'Verifying…',
      differentEmail: 'Use a different email',

      didntReceiveCode: "Didn't receive a code?",
      resendCode: 'Resend code',
      resending: 'Resending…',
      resendAvailableIn:
      'You can request another code in',
      seconds: 'seconds.',

      signedIn: 'Signed in',
      welcomeBack: 'Welcome back',
      signedInAs: 'You are signed in as',

      accessUnavailable: 'Access unavailable',
      accessNotEnabled:
        'CareerVoice access is not enabled',

      serviceUnavailable: 'Service unavailable',
      verifyFailedTitle:
        'We could not verify your CareerVoice account',
      tryAgain: 'Try again',
      tryingAgain: 'Trying again…',

      signOut: 'Sign out',
      signingOut: 'Signing out…',

      errors: {
        expired:
          'Your sign-in session is no longer valid. Please sign in again.',
        denied:
          'This account is not currently approved to use CareerVoice.',
        unavailable:
          'CareerVoice is temporarily unavailable. Please try again shortly.',
        verifyAccount:
          'CareerVoice could not verify your account. Please try again.',
        initialize:
          'Authentication could not be initialized. Please refresh and try again.',
        sendCode:
          'A verification code could not be sent. Check the email address and try again.',
        verifyCode:
          'The verification code could not be confirmed. Check the code and try again.',
        signOut:
          'Sign out failed. Please try again.',
      },
    },

    usage: {
      loading: "Loading today's usage…",
      title: "Today's AI usage",
      remaining: 'units remaining',
      used: 'used',
      unlimited: 'Unlimited AI quota',
      unitsUsed: 'AI units used',
      profileExtractions: 'AI profile extractions',
      voiceTranscriptions: 'voice transcriptions',
      documentRecognitions: 'document recognitions',
      rankingRuns: 'AI ranking runs',
      jobSearches: 'job searches',
      errors: {
        expired:
          'Your session has expired. Please sign in again.',
        denied:
          'Your account does not currently have access to usage information.',
        unavailable:
          'Usage information is temporarily unavailable.',
        generic:
          'Usage information could not be loaded.',
      },
    },

    profile: {
      step: 'Step 1',
      title: 'Build your career profile',
      description:
        'Add your experience, skills, preferences, and career goals.',

      inputMethod: 'Input method',
      textInput: 'Text',
      documentInput: 'Document',
      voiceInput: 'Voice',

      voiceRecording: 'Voice recording',
      voiceHelp:
        'Record your career information, then transcribe and review it. Transcription uses 1 AI unit.',
      startRecording: 'Start recording',
      stopRecording: 'Stop recording',
      recording: 'Recording…',
      transcribeVoice: 'Transcribe recording',
      transcribingVoice: 'Transcribing…',
      voiceTranscript: 'Transcript',
      voiceTranscriptPlaceholder:
        'Your transcript will appear here. You can edit it before creating your career profile.',

      voiceErrors: {
        unsupported:
          'Voice recording is not supported by this browser.',
        microphone:
          'Microphone access could not be started. Check your browser permission and try again.',
        noRecording:
          'Record some audio before transcribing.',
        tooLarge:
          'The voice recording must be 10 MB or smaller.',
        invalid:
          'The voice recording could not be processed. Record it again and retry.',
        expired:
          'Your session has expired. Please sign in again.',
        denied:
          'Your account is not allowed to perform this action.',
        quota:
          'You do not have enough AI allowance remaining to transcribe this recording.',
        unavailable:
          'Voice transcription is temporarily unavailable.',
        generic:
          'Voice transcription failed. Please try again.',
      },

      information: 'Career information',
      placeholder:
        'For example: Junior software developer with Python and React experience, looking for backend roles in Adelaide.',

      document: 'Career document',
      chooseFile: 'Choose file',
      noFileSelected: 'No file selected',
      documentHelp:
        'Upload a TXT, PDF, or DOCX file up to 5 MB.',
      additionalPreferences:
        'Additional preferences (optional)',
      additionalPreferencesPlaceholder:
        'For example: I prefer junior backend roles in Adelaide and hybrid work.',
      imageRecognition:
        'Use AI recognition if this PDF is scanned',
      imageRecognitionHelp:
        'Only used when the PDF has no selectable text. Uses 1 AI unit if recognition runs.',

      extractionMethod: 'Profile extraction',
      standard: 'Standard',
      aiAssisted: 'AI-assisted',
      extract: 'Extract career profile',
      extracting: 'Extracting profile…',
      success: 'Profile ready to review.',

      errors: {
        empty:
          'Enter some career information before continuing.',
        documentMissing:
          'Choose a career document before continuing.',
        documentTooLarge:
          'The document must be 5 MB or smaller.',
        documentInvalid:
          'The uploaded document could not be processed. Check the file and try again.',
        expired:
          'Your session has expired. Please sign in again.',
        denied:
          'Your account is not allowed to perform this action.',
        invalid:
          'The career information could not be processed. Check the input and try again.',
        quota:
          'You do not have enough AI allowance remaining for this request.',
        unavailable:
          'Career profile extraction is temporarily unavailable.',
        generic:
          'Career profile extraction failed. Please try again.',
      },
    },

    profileReview: {
      kicker: 'Profile review',
      title: 'Review your career profile',
      description:
      'Review and edit anything that needs correcting.',
      experienceLevel: 'Experience level',
      targetRoles: 'Target roles',
      skills: 'Skills',
      preferredLocations: 'Preferred locations',
      preferredWorkTypes: 'Preferred work types',
      likedAreas: 'Areas you prefer',
      dislikedAreas: 'Areas you want to avoid',
      hardConstraints: 'Hard constraints',
      careerGoals: 'Career goals',
      notes: 'Other notes',
      add: 'Add',
      remove: 'Remove',
      confirm: 'Confirm profile',
      confirmed: 'Profile confirmed',
      confirmationMessage:
      'Profile confirmed. You can continue to Jobs.',
      placeholders: {
        experienceLevel:
          'For example: Junior, Mid-level, Senior',
        targetRoles:
          'Add a target role',
        skills:
          'Add a skill',
        preferredLocations:
          'Add a preferred location',
        preferredWorkTypes:
          'Add a work type',
        likedAreas:
          'Add an area you prefer',
        dislikedAreas:
          'Add an area you want to avoid',
        hardConstraints:
          'Add a non-negotiable requirement',
        careerGoals:
          'Add a career goal',
        notes:
          'Add another note',
      },
    },

    jobSearch: {
      kicker: 'Step 2',
      title: 'Search for jobs',
      description:
      'Choose the roles and location you want to search.',
      roles: 'Search roles',
      rolesHelp:
      'Up to 3 roles. These start from your profile.',
      role: 'Role',
      addRole: 'Add role',
      removeRole: 'Remove',
      location: 'Location',
      locationPlaceholder:
      'For example: Adelaide',
      locationHelp:
      'Leave blank to search all locations.',
      resultsPerRole: 'Results per role',
      resultsHelp:
      'Choose 1–10 listings per role.',
      source: 'Job source',
      adzuna: 'Adzuna',
      search: 'Search jobs',
      searching: 'Searching…',
      success: 'Job search completed.',
      found: 'job(s) found.',
      errors: {
        noRoles:
          'Add at least one search role before continuing.',
        tooManyRoles:
          'You can search for at most 3 roles.',
        invalidResults:
          'Results per role must be between 1 and 10.',
        expired:
          'Your session has expired. Please sign in again.',
        denied:
          'Your account is not allowed to perform this action.',
        invalid:
          'The job-search settings could not be processed. Check them and try again.',
        unavailable:
          'Job search is temporarily unavailable.',
        generic:
          'Job search failed. Please try again.',
      },
    },

    jobResults: {
      kicker: 'Search results',
      title: 'Job listings',
      found: 'job(s) found',
      empty:
        'No matching job listings were returned for this search.',
      location: 'Location',
      source: 'Source',
      requiredSkills: 'Required skills',
      preferredSkills: 'Preferred skills',
      responsibilities: 'Responsibilities',
      description: 'Description',
      tags: 'Tags',
      details: 'View job details',
      viewListing: 'View original listing',
      adzuna: 'Adzuna',

      workTypes: {
        remote: 'Remote',
        hybrid: 'Hybrid',
        onsite: 'On-site',
        unknown: 'Work type unknown',
      },

      seniority: {
        intern: 'Intern',
        junior: 'Junior',
        mid: 'Mid-level',
        senior: 'Senior',
        lead: 'Lead',
        unknown: 'Seniority unknown',
      },
    },

    recommendations: {
      kicker: 'Step 3',
      title: 'Generate recommendations',
      description:
      'Choose how you want to rank the jobs.',
      rankingMethod: 'Ranking method',
      standard: 'Standard',
      aiAssisted: 'AI-assisted',
      standardHelp:
      'Rule-based ranking. Uses no AI units.',
      aiHelp:
      'AI-assisted ranking. Uses 10 AI units per run.',
      maxResults: 'Recommendations to return',
      maxResultsHelp:
      'Return up to 10 recommendations.',
      excludeRejected:
      'Exclude jobs rejected by hard constraints',
      excludeRejectedHelp:
      'Hide jobs that conflict with your hard constraints.',
      generate: 'Generate recommendations',
      generating: 'Generating recommendations…',
      success: 'Recommendations generated successfully.',
      returned: 'recommendation(s) returned.',
      errors: {
        invalidResults:
          'The number of recommendations must be between 1 and 10.',
        expired:
          'Your session has expired. Please sign in again.',
        denied:
          'Your account is not allowed to perform this action.',
        invalid:
          'The recommendation settings could not be processed. Check them and try again.',
        quota:
          'You do not have enough AI allowance remaining for AI-assisted ranking.',
        unavailable:
          'Recommendation generation is temporarily unavailable.',
        generic:
          'Recommendation generation failed. Please try again.',
      },
      availableJobs: 'Available jobs',
      maximumRecommendations: 'Maximum recommendations',
    },

    recommendationResults: {
      kicker: 'Recommendations',
      title: 'Your recommended jobs',
      returned: 'recommendation(s)',
      jobsScored: 'Jobs evaluated',
      jobsScoredWithAi: 'Jobs evaluated with AI',
      rankingMethod: 'Ranking method',
      standard: 'Standard',
      aiAssisted: 'AI-assisted',
      rank: 'Rank',
      matchScore: 'Match score',
      reasons: 'Why this job matches',
      missingSkills: 'Missing skills',
      penalties: 'Match concerns',
      uncertainties: 'Uncertainties',
      constraintConflict:
        'Hard-constraint conflict',
      constraintConflictDescription:
        'This job conflicts with one or more of your non-negotiable requirements.',
      empty:
        'No recommendations were returned with the current settings.',
    },
  },

  'zh-CN': {
    language: {
      select: '选择语言',
    },

    sidebar: {
      show: '打开侧边栏',
      hide: '关闭侧边栏',
      navigation: '求职流程',
      profile: '职业画像',
      jobs: '职位',
      matches: '匹配推荐',
      account: '账户',
    },

    navigation: {
      backToProfile: '← 返回职业画像',
      nextToJobs: '下一步：职位 →',
      backToJobs: '← 返回职位',
      nextToMatches: '下一步：匹配推荐 →',
    },

    app: {
      signOut: '退出登录',
      signingOut: '正在退出…',
      signOutError: '退出登录失败，请重试。',
      profileExtracted: '职业画像已生成',
      readyForReview: '可以开始检查',
      targetRoles: '个目标岗位',
      skillsIdentified: '项技能已识别。',
      productSummary:
      '建立职业画像，搜索职位，并比较个性化匹配结果。',
    },

    auth: {
      checking: '正在检查登录状态…',
      privateTesting: '受限测试',
      signInTitle: '登录 CareerVoice',
      approvedEmail:
        '输入已获批准的邮箱地址以接收验证码。',
      email: '邮箱地址',
      sendCode: '发送验证码',
      sending: '正在发送…',

      verification: '邮箱验证',
      enterCode: '输入验证码',
      codeSentTo: '验证码已发送至',
      code: '验证码',
      codeSent: '验证码已发送到你的邮箱。',
      verify: '验证并登录',
      verifying: '正在验证…',
      differentEmail: '使用其他邮箱',

      didntReceiveCode: '没有收到验证码？',
      resendCode: '重新发送验证码',
      resending: '正在重新发送…',
      resendAvailableIn:
      '你可以在以下时间后重新发送验证码：',
      seconds: '秒。',

      signedIn: '已登录',
      welcomeBack: '欢迎回来',
      signedInAs: '当前登录账号',

      accessUnavailable: '无法访问',
      accessNotEnabled:
        'CareerVoice 访问权限尚未启用',

      serviceUnavailable: '服务暂不可用',
      verifyFailedTitle:
        '无法验证你的 CareerVoice 账号',
      tryAgain: '重试',
      tryingAgain: '正在重试…',

      signOut: '退出登录',
      signingOut: '正在退出…',

      errors: {
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '此账号目前未获批准使用 CareerVoice。',
        unavailable:
          'CareerVoice 暂时不可用，请稍后重试。',
        verifyAccount:
          '无法验证你的 CareerVoice 账号，请重试。',
        initialize:
          '无法初始化登录状态，请刷新页面后重试。',
        sendCode:
          '无法发送验证码，请检查邮箱地址后重试。',
        verifyCode:
          '无法确认验证码，请检查验证码后重试。',
        signOut:
          '退出登录失败，请重试。',
      },
    },

    usage: {
      loading: '正在加载今日使用情况…',
      title: '今日 AI 辅助额度',
      remaining: '个 AI 单位剩余',
      used: '已使用',
      unlimited: '无限 AI 配额',
      unitsUsed: '已使用的 AI 单位',
      profileExtractions: 'AI 职业画像生成',
      voiceTranscriptions: '语音转文字',
      documentRecognitions: '文档识别',
      rankingRuns: 'AI 职位排序',
      jobSearches: '职位搜索',
      errors: {
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '你的账号目前无法查看使用情况。',
        unavailable:
          '使用情况暂时无法获取。',
        generic:
          '无法加载使用情况。',
      },
    },

    profile: {
      step: '步骤 1',
      title: '建立你的职业画像',
      description:
        '填写你的经历、技能、偏好和职业目标。',

      inputMethod: '输入方式',
      textInput: '文字',
      documentInput: '文档',
      voiceInput: '语音',
      voiceRecording: '语音录制',
      voiceHelp:
        '录制你的职业信息，然后转写并检查内容。语音转写消耗 1 个 AI 单位。',
      startRecording: '开始录音',
      stopRecording: '停止录音',
      recording: '正在录音…',
      transcribeVoice: '转写录音',
      transcribingVoice: '正在转写…',
      voiceTranscript: '转写文本',
      voiceTranscriptPlaceholder:
        '转写结果会显示在这里。生成职业画像前可以进行修改。',

      voiceErrors: {
        unsupported:
          '当前浏览器不支持语音录制。',
        microphone:
          '无法启动麦克风，请检查浏览器权限后重试。',
        noRecording:
          '请先录制语音再进行转写。',
        tooLarge:
          '语音录音大小不能超过 10 MB。',
        invalid:
          '无法处理该语音录音，请重新录制后重试。',
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '你的账号目前无法执行此操作。',
        quota:
          '当前剩余 AI 额度不足以转写这段录音。',
        unavailable:
          '语音转写服务暂时不可用。',
        generic:
          '语音转写失败，请重试。',
      },

      information: '职业信息与偏好',
      placeholder:
        '例如：初级软件开发人员，掌握 Python 和 React，希望在阿德莱德寻找后端岗位……',

      document: '职业文档',
      chooseFile: '选择文件',
      noFileSelected: '尚未选择文件',
      documentHelp:
        '上传不超过 5 MB 的 TXT、PDF 或 DOCX 文件。',
      additionalPreferences:
        '补充偏好（可选）',
      additionalPreferencesPlaceholder:
        '例如：希望在阿德莱德寻找初级后端岗位，并偏好混合办公。',
      imageRecognition:
        '如果 PDF 是扫描件，使用 AI 识别',
      imageRecognitionHelp:
        '仅在 PDF 没有可选文字时使用；实际进行识别时消耗 1 个 AI 单位。',

      extractionMethod: '职业画像生成方式',
      standard: '标准',
      aiAssisted: 'AI 辅助',
      extract: '生成职业画像',
      extracting: '正在生成职业画像…',
      success: '职业画像已生成，可以开始检查。',

      errors: {
        empty:
          '请输入职业信息后再继续。',
        documentMissing:
          '请选择职业文档后再继续。',
        documentTooLarge:
          '文档大小不能超过 5 MB。',
        documentInvalid:
          '无法处理上传的文档，请检查文件后重试。',
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '你的账号目前无法执行此操作。',
        invalid:
          '无法处理这些职业信息，请检查输入后重试。',
        quota:
          '当前剩余 AI 额度不足以执行此操作。',
        unavailable:
          '职业画像生成服务暂时不可用。',
        generic:
          '职业画像生成失败，请重试。',
      },
    },

    profileReview: {
      kicker: '职业画像复核',
      title: '检查并修改你的职业画像',
      description:
      '检查并修改需要更正的内容。',
      experienceLevel: '经验水平',
      targetRoles: '目标岗位',
      skills: '技能',
      preferredLocations: '偏好地区',
      preferredWorkTypes: '偏好工作方式',
      likedAreas: '感兴趣的方向',
      dislikedAreas: '希望避开的方向',
      hardConstraints: '不可妥协的条件',
      careerGoals: '职业目标',
      notes: '其他备注',
      add: '添加',
      remove: '删除',
      confirm: '确认职业画像',
      confirmed: '职业画像已确认',
      confirmationMessage:
      '职业画像已确认，可以继续搜索职位。',
      placeholders: {
        experienceLevel:
          '例如：初级、中级、高级',
        targetRoles:
          '添加目标岗位',
        skills:
          '添加技能',
        preferredLocations:
          '添加偏好地区',
        preferredWorkTypes:
          '添加工作方式',
        likedAreas:
          '添加感兴趣的方向',
        dislikedAreas:
          '添加希望避开的方向',
        hardConstraints:
          '添加不可妥协的条件',
        careerGoals:
          '添加职业目标',
        notes:
          '添加其他备注',
      },
    },

    jobSearch: {
      kicker: '步骤 2',
      title: '搜索职位',
      description:
      '选择要搜索的岗位和地区。',
      roles: '搜索岗位',
      rolesHelp:
      '最多 3 个岗位，默认来自你的职业画像。',
      role: '岗位',
      addRole: '添加岗位',
      removeRole: '删除',
      location: '地区',
      locationPlaceholder:
      '例如：Adelaide',
      locationHelp:
      '留空则不限制地区。',
      resultsPerRole: '每个岗位的结果数量',
      resultsHelp:
      '每个岗位返回 1–10 条职位。',
      source: '职位来源',
      adzuna: 'Adzuna',
      search: '搜索职位',
      searching: '正在搜索…',
      success: '职位搜索完成。',
      found: '个职位已找到。',
      errors: {
        noRoles:
          '继续之前，请至少添加一个搜索岗位。',
        tooManyRoles:
          '最多只能搜索 3 个岗位。',
        invalidResults:
          '每个岗位的结果数量必须在 1 至 10 之间。',
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '你的账号目前无法执行此操作。',
        invalid:
          '无法处理这些职位搜索设置，请检查后重试。',
        unavailable:
          '职位搜索服务暂时不可用。',
        generic:
          '职位搜索失败，请重试。',
      },
    },

    jobResults: {
      kicker: '搜索结果',
      title: '职位列表',
      found: '个职位',
      empty:
        '本次搜索没有返回匹配的职位信息。',
      location: '地区',
      source: '来源',
      requiredSkills: '必需技能',
      preferredSkills: '优先技能',
      responsibilities: '岗位职责',
      description: '职位描述',
      tags: '标签',
      details: '查看职位详情',
      viewListing: '查看原始职位页面',
      adzuna: 'Adzuna',

      workTypes: {
        remote: '远程',
        hybrid: '混合办公',
        onsite: '现场办公',
        unknown: '工作方式未知',
      },

      seniority: {
        intern: '实习',
        junior: '初级',
        mid: '中级',
        senior: '高级',
        lead: '负责人级别',
        unknown: '经验级别未知',
      },
    },

    recommendations: {
      kicker: '步骤 3',
      title: '生成职位推荐',
      description:
      '选择职位排序方式。',
      rankingMethod: '排序方式',
      standard: '标准',
      aiAssisted: 'AI 辅助',
      standardHelp:
      '规则排序，不消耗 AI 单位。',
      aiHelp:
      'AI 辅助排序，每次消耗 10 个 AI 单位。',
      maxResults: '返回的推荐数量',
      maxResultsHelp:
      '最多返回 10 个推荐结果。',
      excludeRejected:
      '排除违反不可妥协条件的职位',
      excludeRejectedHelp:
      '隐藏与不可妥协条件冲突的职位。',
      generate: '生成职位推荐',
      generating: '正在生成推荐…',
      success: '职位推荐生成成功。',
      returned: '个推荐职位。',
      errors: {
        invalidResults:
          '推荐数量必须在 1 至 10 之间。',
        expired:
          '登录状态已失效，请重新登录。',
        denied:
          '你的账号目前无法执行此操作。',
        invalid:
          '无法处理这些推荐设置，请检查后重试。',
        quota:
          '当前剩余 AI 额度不足以进行 AI 辅助排序。',
        unavailable:
          '职位推荐服务暂时不可用。',
        generic:
          '职位推荐生成失败，请重试。',
      },
      availableJobs: '可用职位',
      maximumRecommendations: '最多推荐数量',
    },

    recommendationResults: {
      kicker: '职位推荐',
      title: '为你推荐的职位',
      returned: '个推荐职位',
      jobsScored: '已评估职位',
      jobsScoredWithAi: 'AI 已评估职位',
      rankingMethod: '排序方式',
      standard: '标准',
      aiAssisted: 'AI 辅助',
      rank: '排名',
      matchScore: '匹配分数',
      reasons: '推荐原因',
      missingSkills: '缺失技能',
      penalties: '匹配风险',
      uncertainties: '不确定信息',
      constraintConflict:
        '存在不可妥协条件冲突',
      constraintConflictDescription:
        '此职位与你的一项或多项不可妥协要求存在冲突。',
      empty:
        '当前设置下没有返回推荐职位。',
    },
  },
} as const

export function loadAppLanguage(): AppLanguage {
  const storedLanguage =
    window.localStorage.getItem(
      LANGUAGE_STORAGE_KEY,
    )

  return storedLanguage === 'zh-CN'
    ? 'zh-CN'
    : 'en'
}

export function saveAppLanguage(
  language: AppLanguage,
): void {
  window.localStorage.setItem(
    LANGUAGE_STORAGE_KEY,
    language,
  )
}