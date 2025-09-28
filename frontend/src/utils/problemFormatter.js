/**
 * 题目格式化工具
 * 将用户输入的题目信息转换成统一的HTML格式
 */

/**
 * 生成统一格式的题目HTML
 * @param {Object} problemData - 题目数据
 * @param {string} problemData.name - 题目名称
 * @param {string} problemData.chineseName - 中文名称
 * @param {string} problemData.description - 题目描述
 * @param {string} problemData.inputFormat - 输入格式
 * @param {string} problemData.outputFormat - 输出格式
 * @param {string} problemData.sampleInput - 样例输入
 * @param {string} problemData.sampleOutput - 样例输出
 * @param {string} problemData.dataRange - 数据范围
 * @param {string} problemData.note - 备注
 * @returns {string} 格式化后的HTML
 */
export function generateProblemHTML(problemData) {
  const {
    name = '',
    chineseName = '',
    description = '',
    inputFormat = '',
    outputFormat = '',
    sampleInput = '',
    sampleOutput = '',
    dataRange = '',
    note = ''
  } = problemData;

  // 转义HTML特殊字符
  const escapeHtml = (text) => {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  };

  // 格式化文本，保留换行
  const formatText = (text) => {
    if (!text) return '';
    return escapeHtml(text).replace(/\n/g, '</br>　　');
  };

  const html = `<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>题目</title>
    <style type="text/css">
        .SimSun {
            font-size: 14px;
            font-family: 宋体;
        }
        body {
            background: #FFFFFF;
            margin: 0;
            padding: 0;
        }
        .container {
            margin: 0px auto;
            width: 1000px;
            padding: 20px;
        }
        .title {
            font-family: 宋体;
            font-size: 18px;
            font-weight: bold;
            color: Green;
            text-align: center;
            margin-bottom: 20px;
        }
        .section-title {
            font-family: 宋体;
            font-size: 16px;
            font-weight: bold;
            color: Green;
            margin-left: 20px;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        .content {
            line-height: 22px;
            margin-left: 20px;
            margin-right: 20px;
            text-indent: 2em;
        }
        .note-text {
            color: #FF0000;
        }
        .sample-data {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 5px;
            border: 1px solid #ddd;
            margin: 5px 0;
            text-indent: 0;
        }
    </style>
</head>

<body>
    <div class="container">
        <p class="title">${escapeHtml(chineseName || name)}</p>
        
        ${description ? `
        <p class="section-title">题目描述</p>
        <p class="SimSun content">${formatText(description)}</p>
        ` : ''}
        
        ${inputFormat ? `
        <p class="section-title">输入</p>
        <p class="SimSun content">${formatText(inputFormat)}</p>
        ` : ''}
        
        ${outputFormat ? `
        <p class="section-title">输出</p>
        <p class="SimSun content">${formatText(outputFormat)}</p>
        ` : ''}
        
        ${sampleInput ? `
        <p class="section-title">输入示例</p>
        <div class="SimSun content">
            <div class="sample-data">${escapeHtml(sampleInput)}</div>
        </div>
        ` : ''}
        
        ${sampleOutput ? `
        <p class="section-title">输出示例</p>
        <div class="SimSun content">
            <div class="sample-data">${escapeHtml(sampleOutput)}</div>
        </div>
        ` : ''}
        
        ${dataRange ? `
        <p class="section-title">数据范围</p>
        <p class="SimSun content">${formatText(dataRange)}</p>
        ` : ''}
        
        ${note ? `
        <p class="section-title">注意</p>
        <p class="SimSun content"><span class="note-text">${formatText(note)}</span></p>
        ` : ''}
    </div>
</body>
</html>`;

  return html;
}

/**
 * 解析现有的题目描述文本，尝试提取结构化信息
 * @param {string} description - 原始题目描述
 * @returns {Object} 解析后的结构化数据
 */
export function parseDescription(description) {
  if (!description) return {};

  const sections = {};
  const lines = description.split('\n');
  let currentSection = 'description';
  let content = [];

  // 常见的章节标识符 - 按优先级排序，更具体的模式在前
  const sectionPatterns = {
    sampleInput: /^(输入示例)[:：]?/i,
    sampleOutput: /^(输出示例)[:：]?/i,
    inputFormat: /^(输入)[:：]?/i,
    outputFormat: /^(输出)[:：]?/i,
    description: /^(题目描述)[:：]?/i,
    dataRange: /^(数据范围)[:：]?/i,
    note: /^(注意|备注|说明)[:：]?/i
  };

  for (const line of lines) {
    const trimmedLine = line.trim();
    
    // 检查是否是新的章节
    let foundSection = null;
    for (const [section, pattern] of Object.entries(sectionPatterns)) {
      if (pattern.test(trimmedLine)) {
        foundSection = section;
        break;
      }
    }

    if (foundSection) {
      // 保存当前章节内容
      if (content.length > 0) {
        sections[currentSection] = content.join('\n').trim();
      }
      
      // 开始新章节
      currentSection = foundSection;
      content = [];
      
      // 如果这行除了标题还有内容，也要包含进去
      const contentAfterTitle = trimmedLine.replace(sectionPatterns[foundSection], '').trim();
      if (contentAfterTitle) {
        content.push(contentAfterTitle);
      }
    } else {
      // 添加到当前章节
      content.push(line);
    }
  }

  // 保存最后一个章节
  if (content.length > 0) {
    sections[currentSection] = content.join('\n').trim();
  }

  return sections;
}

/**
 * 智能格式化题目描述
 * 如果描述中包含结构化信息，则提取并格式化；否则作为普通描述处理
 * @param {Object} problemData - 原始题目数据
 * @returns {string} 格式化后的HTML
 */
export function smartFormatProblem(problemData) {
  const { description } = problemData;
  
  // 尝试解析描述中的结构化信息
  const parsedSections = parseDescription(description);
  
  // 合并解析出的信息和原有的信息
  const mergedData = {
    ...problemData,
    ...parsedSections
  };

  return generateProblemHTML(mergedData);
} 