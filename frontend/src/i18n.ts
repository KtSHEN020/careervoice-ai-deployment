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
    },

    app: {
      headline: 'Find roles that fit your career goals',
      description:
        'Build your career profile, search for relevant jobs, and get personalized recommendations based on your skills and preferences.',
      signOut: 'Sign out',
      signingOut: 'Signing out…',
      signOutError: 'Sign out failed. Please try again.',
      profileExtracted: 'Profile extracted',
      readyForReview: 'Ready for review',
      targetRoles: 'target role(s)',
      skillsIdentified: 'skill(s) identified.',
      workflowProfileTitle: 'Build your career profile',
      workflowProfileDescription:
        'Tell us about your skills, preferences, and career goals.',
      workflowJobsTitle: 'Search for jobs',
      workflowJobsDescription:
        'Search across the roles and locations you are interested in.',
      workflowRecommendationsTitle:
        'Get personalized recommendations',
      workflowRecommendationsDescription:
        'Compare jobs using match explanations, missing skills, and preference-aware scoring.',
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
        'Describe your experience, skills, preferred roles, locations, work preferences, and career goals.',
      information: 'Career information',
      placeholder:
        'For example: I am a junior software developer with Python and React experience. I am looking for backend or full-stack roles in Adelaide...',
      extractionMethod: 'Profile extraction',
      standard: 'Standard',
      aiAssisted: 'AI-assisted',
      extract: 'Extract career profile',
      extracting: 'Extracting profile…',
      success: 'Career profile extracted successfully.',
      errors: {
        empty:
          'Enter some career information before continuing.',
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
        'Check the extracted information and correct anything that is missing or inaccurate before continuing.',
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
        'Your reviewed profile is ready to be used for job search.',
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
        'Review the search settings generated from your confirmed career profile, then search for current job listings.',
      roles: 'Search roles',
      rolesHelp:
        'You can search for up to 3 roles. These are initially taken from your confirmed target roles.',
      role: 'Role',
      addRole: 'Add role',
      removeRole: 'Remove',
      location: 'Location',
      locationPlaceholder:
        'For example: Adelaide',
      locationHelp:
        'Leave this blank if you do not want to restrict the search by location.',
      resultsPerRole: 'Results per role',
      resultsHelp:
        'Choose between 1 and 10 listings for each role.',
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
  },

  'zh-CN': {
    language: {
      select: '选择语言',
    },

    sidebar: {
      show: '打开侧边栏',
      hide: '关闭侧边栏',
    },

    app: {
      headline: '找到符合你职业目标的岗位',
      description:
        '建立职业画像，搜索相关职位，并根据你的技能和偏好获得个性化推荐。',
      signOut: '退出登录',
      signingOut: '正在退出…',
      signOutError: '退出登录失败，请重试。',
      profileExtracted: '职业画像已生成',
      readyForReview: '可以开始检查',
      targetRoles: '个目标岗位',
      skillsIdentified: '项技能已识别。',
      workflowProfileTitle: '建立你的职业画像',
      workflowProfileDescription:
        '提供你的技能、偏好和职业目标。',
      workflowJobsTitle: '搜索职位',
      workflowJobsDescription:
        '根据你感兴趣的岗位和地区搜索职位。',
      workflowRecommendationsTitle: '获取个性化推荐',
      workflowRecommendationsDescription:
        '通过匹配说明、缺失技能和偏好评分比较职位。',
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
        '描述你的工作经历、技能、目标岗位、地区、工作方式偏好和职业目标。',
      information: '职业信息与偏好',
      placeholder:
        '例如：我是一名初级软件开发人员，有 Python 和 React 经验，希望在阿德莱德寻找后端或全栈开发岗位……',
      extractionMethod: '职业画像生成方式',
      standard: '标准',
      aiAssisted: 'AI 辅助',
      extract: '生成职业画像',
      extracting: '正在生成职业画像…',
      success: '职业画像生成成功。',
      errors: {
        empty:
          '请输入职业信息后再继续。',
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
        '在继续之前，请检查提取的信息，并补充或修改任何遗漏或不准确的内容。',
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
        '你已完成职业画像复核，可以用于后续职位搜索。',
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
        '检查根据已确认职业画像生成的搜索设置，然后搜索当前职位信息。',
      roles: '搜索岗位',
      rolesHelp:
        '最多可以搜索 3 个岗位。初始内容来自你已确认的目标岗位。',
      role: '岗位',
      addRole: '添加岗位',
      removeRole: '删除',
      location: '地区',
      locationPlaceholder:
        '例如：Adelaide',
      locationHelp:
        '如果不希望按地区限制搜索，可以留空。',
      resultsPerRole: '每个岗位的结果数量',
      resultsHelp:
        '每个岗位可以搜索 1 至 10 条职位信息。',
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