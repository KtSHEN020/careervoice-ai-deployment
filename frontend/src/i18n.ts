export type AppLanguage = 'en' | 'zh-CN'

const LANGUAGE_STORAGE_KEY = 'careervoice-language'

export const UI_TEXT = {
  en: {
    language: {
      select: 'Select language',
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
  },

  'zh-CN': {
    language: {
      select: '选择语言',
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