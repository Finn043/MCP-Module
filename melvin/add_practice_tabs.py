#!/usr/bin/env python3
"""
Script to add Coding Practice tab to all melvin lessons
"""

import re
from pathlib import Path

# Coding Practice CSS template
PRACTICE_CSS = '''
/* Coding Practice Styles */
.practice-section{margin:24px 0;padding:20px;background:#252526;border-radius:10px;border:1px solid #3e3e42;}
.practice-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.practice-title{color:#9cdcfe;font-size:18px;font-weight:600;}
.practice-badge{padding:4px 12px;border-radius:4px;font-size:12px;font-weight:600;}
.practice-badge.pending{background:#3e3e42;color:#858585;}
.practice-badge.completed{background:#1a3a2a;color:#4ec9b0;}
.practice-badge.viewed{background:#3a3a1a;color:#ffd700;}
.practice-desc{color:#d4d4d4;margin-bottom:16px;line-height:1.7;font-size:14px;}
.code-editor{background:#1e1e1e;border:2px solid #3e3e42;border-radius:6px;padding:14px;font-family:'Courier New',monospace;font-size:14px;color:#d4d4d4;min-height:120px;resize:vertical;transition:border-color 0.2s;width:100%;}
.code-editor:focus{outline:none;border-color:#007acc;}
.code-editor::placeholder{color:#858585;}
.code-output{margin-top:12px;padding:12px 16px;border-radius:6px;font-size:14px;display:none;}
.code-output.show{display:block;}
.code-output.success{background:#1a3a2a;color:#4ec9b0;border:1px solid #4ec9b0;}
.code-output.error{background:#3a3a1a;color:#f44747;border:1px solid #f44747;}
.solution-box{margin-top:16px;display:none;}
.solution-box.show{display:block;}
.solution-content{background:#1a1a2e;border-left:4px solid #ffd700;padding:14px;border-radius:6px;}
.solution-label{color:#ffd700;font-weight:600;margin-bottom:8px;font-size:13px;}
.solution-code{background:#1e1e1e;padding:12px;border-radius:4px;font-family:'Courier New',monospace;font-size:13px;color:#9cdcfe;}
.practice-actions{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap;}
.btn-check{padding:10px 20px;background:#007acc;color:white;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;transition:background 0.2s;}
.btn-check:hover{background:#005f9e;}
.btn-hint{padding:10px 20px;background:#2d2d30;color:#ffd700;border:1px solid #3e3e42;border-radius:6px;cursor:pointer;font-size:14px;transition:background 0.2s;}
.btn-hint:hover{background:#3e3e42;}
.btn-solution{padding:10px 20px;background:#2d2d30;color:#858585;border:1px solid #3e3e42;border-radius:6px;cursor:pointer;font-size:14px;transition:all 0.2s;}
.btn-solution:hover{border-color:#ffd700;color:#ffd700;}
.xp-section{margin-top:30px;padding:20px;background:#2d2d30;border-radius:8px;border:1px solid #3e3e42;}
.xp-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
.xp-label{color:#fff;font-weight:600;font-size:15px;}
.xp-count{color:#4ec9b0;font-size:16px;font-weight:700;}
.xp-bar-container{height:8px;background:#1e1e1e;border-radius:4px;overflow:hidden;}
.xp-bar-fill{height:100%;background:#4ec9b0;width:0%;transition:width 0.3s ease;}
.xp-text{margin-top:8px;color:#858585;font-size:13px;}
.hint-box{margin-top:12px;padding:12px;background:#2d2d30;border-left:3px solid #ffc107;border-radius:4px;display:none;font-size:13px;color:#d4d4d4;}
.hint-box.show{display:block;}
.mcq-options{display:grid;gap:12px;margin-top:16px;}
.mcq-option{background:#2d2d30;border:2px solid #3e3e42;border-radius:6px;padding:14px 16px;cursor:pointer;transition:all 0.2s;}
.mcq-option:hover{border-color:#007acc;background:#2a3a4a;}
.mcq-option.selected{border-color:#007acc;background:#1e3a5f;}
.mcq-option.correct{border-color:#4ec9b0;background:#1a3a2a;}
.mcq-option.wrong{border-color:#f44747;background:#3a1a1a;}
'''

# JavaScript functions for coding practice
PRACTICE_JS = '''
	// ========== Coding Practice ==========
	const exercises = {1: {completed: false, viewed: false}, 2: {completed: false, viewed: false}};

	function loadPracticeProgress() {
	  const lessonId = getLessonId();
	  const totalExercises = getTotalExercises();
	  let completedCount = 0;

	  for (let i = 1; i <= totalExercises; i++) {
	    const key = `mcp_${lessonId}_ex_${i}`;
	    const saved = localStorage.getItem(key);
	    if (saved) {
	      exercises[i] = JSON.parse(saved);
	      if (exercises[i].completed) completedCount++;
	      updateExerciseBadge(i);
	    }
	  }
	  updateXPBar(completedCount, totalExercises);
	}

	function getLessonId() {
	  const match = window.location.pathname.match(/lesson-(\\d+)/);
	  return match ? match[1] : '00';
	}

	function getTotalExercises() {
	  return document.querySelectorAll('.practice-block').length;
	}

	function updateExerciseBadge(num) {
	  const badge = document.getElementById(`badge-${num}`);
	  if (!badge) return;

	  if (exercises[num].completed) {
	    badge.className = 'practice-badge completed';
	    badge.textContent = '✅ Hoàn thành';
	  } else if (exercises[num].viewed) {
	    badge.className = 'practice-badge viewed';
	    badge.textContent = '📝 Đã xem';
	  }
	}

	function updateXPBar(completed, total) {
	  const percent = Math.round((completed / total) * 100);
	  document.getElementById('xp-fill').style.width = percent + '%';
	  document.getElementById('xp-count').textContent = `${completed}/${total}`;
	  document.getElementById('xp-text').textContent = percent === 100 ? 'Hoàn tất cả!' : `Còn ${total - completed} bài tập`;
	}

	function savePracticeProgress(num, completed) {
	  const lessonId = getLessonId();
	  const key = `mcp_${lessonId}_ex_${num}`;
	  if (completed) {
	    exercises[num].completed = true;
	  } else {
	    exercises[num].viewed = true;
	  }
	  localStorage.setItem(key, JSON.stringify(exercises[num]));
	  updateExerciseBadge(num);

	  if (completed) {
	    const total = getTotalExercises();
	    const completedCount = Object.values(exercises).filter(e => e.completed).length;
	    updateXPBar(completedCount, total);
	  }
	}

	function showHint(num) {
	  const hint = document.getElementById(`hint-${num}`);
	  if (hint) hint.classList.toggle('show');
	}

	function showSolution(num) {
	  const solution = document.getElementById(`solution-${num}`);
	  const output = document.getElementById(`output-${num}`);

	  if (solution) {
	    solution.classList.toggle('show');
	    if (solution.classList.contains('show')) {
	      savePracticeProgress(num, false);
	      if (output) {
	        output.className = 'code-output show';
	        output.innerHTML = '📋 <strong>Đã xem giải pháp.</strong> Hãy thử làm lại trước khi xem kết quả!';
	      }
	    }
	  }
	}
'''

# XP section template
XP_SECTION = '''    <div class="xp-section">
      <div class="xp-header">
        <span class="xp-label">Tiến độ bài tập</span>
        <span class="xp-count" id="xp-count">0/2</span>
      </div>
      <div class="xp-bar-container">
        <div class="xp-bar-fill" id="xp-fill"></div>
      </div>
      <div class="xp-text" id="xp-text">Hoàn tất cả bài tập để tiếp tục!</div>
    </div>'''

# Placeholder exercise for lessons without specific exercises yet
PLACEHOLDER_EXERCISE = '''    <!-- EXERCISE 1: Placeholder -->
    <div class="practice-block" id="exercise-1">
      <div class="practice-header">
        <span class="practice-title">Bài tập 1: {EXERCISE_TITLE}</span>
        <span class="practice-badge pending" id="badge-1">⬜ Chưa làm</span>
      </div>
      <p class="practice-desc">
        {EXERCISE_DESC}
      </p>
      <div id="hint-1" class="hint-box">
        💡 <strong>Gợi ý:</strong> {EXERCISE_HINT}
      </div>
      <div id="output-1" class="code-output"></div>
      <div class="practice-actions">
        <button class="btn-check" onclick="checkExercise(1)">✓ Kiểm tra</button>
        <button class="btn-hint" onclick="showHint(1)">💡 Gợi ý</button>
      </div>
    </div>'''


def add_practice_tab(file_path: Path):
    """Add Coding Practice tab to a lesson file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if practice tab already exists
    if '<div id="tab-practice"' in content:
        print(f"  Skipping {file_path.name} - already has practice tab")
        return

    # Add practice tab to tabs section
    tabs_pattern = r'(<div class="tabs">\s*<div class="tab" onclick="switchTab\(\'theory\'\)">Lý thuyết</div>\s*<div class="tab" onclick="switchTab\(\'demo\'\)">Demo</div>)'
    tabs_replacement = r'''\\1    <div class="tab active" onclick="switchTab('theory')">Lý thuyết</div>
\\2    <div class="tab" onclick="switchTab('demo')">Demo</div>
\\3    <div class="tab" onclick="switchTab('practice')">Luyện tập Code</div>
\\4    <div class="tab" onclick="switchTab('quiz')">Quiz</div>
'''

    content = re.sub(tabs_pattern, tabs_replacement, content)

    # Add CSS if not present
    if 'practice-section' not in content:
        # Find end of style tag
        style_end = content.find('</style>')
        if style_end:
            content = content[:style_end] + PRACTICE_CSS + content[style_end:]

    # Add practice tab content before quiz tab
    quiz_tab = '<div id="tab-quiz" class="tab-content">'
    practice_tab_placeholder = '<div id="tab-practice" class="tab-content">'
    practice_tab_placeholder += XP_SECTION
    practice_tab_placeholder += '  <!-- TODO: Add exercises -->'
    practice_tab_placeholder += '</div>'
    practice_tab_placeholder += '\n'

    content = content.replace(quiz_tab, practice_tab_placeholder + quiz_tab)

    # Update switchTab function to include 'practice'
    switch_pattern = r"var tabs = \['theory','demo','quiz'\];"
    switch_replacement = "var tabs = ['theory','demo','practice','quiz'];"
    content = re.sub(switch_pattern, switch_replacement, content)

    # Add loadPracticeProgress() to DOMContentLoaded
    dom_pattern = r'(renderQuiz\(\);)'
    dom_replacement = r'\1\n\tloadPracticeProgress();'
    content = re.sub(dom_pattern, dom_replacement, content)

    # Add checkExercise stub
    if 'function checkExercise' not in content:
        # Find place to add - after loadPracticeProgress
        practice_content = '<div id="tab-practice"'
        if practice_content in content:
            idx = content.find(practice_content)
            # Find end of practice tab
            end_idx = content.find('</div>', idx)
            if end_idx != -1:
                # Add checkExercise function before closing </div>
                end_div = '</div>'
                stub_function = '''

\tfunction checkExercise(num) {
\t  const output = document.getElementById(`output-${num}`);
\t  output.innerHTML = '🔧 <strong>Đang phát triển...</strong><br>Bài tập này sẽ được thêm trong phiên bản sau.';
\t  output.className = 'code-output show';
\t}
'''
                content = content[:end_idx] + stub_function + content[end_idx:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✓ Added practice tab to {file_path.name}")


def main():
    """Process all lesson files"""

    melvin_dir = Path('/Users/luongbaotin/Desktop/School/practice/learning/mcp-basics/melvin')

    # Lessons to process (04-20)
    lessons = [
        'lesson-04-mcp-initialize.html',
        'lesson-05-mcp-tools.html',
        'lesson-06-mcp-resources.html',
        'lesson-07-mcp-prompts.html',
        'lesson-08-primitive-comparison.html',
        'lesson-09-mcp-json-messages.html',
        'lesson-10-stdio-transport.html',
        'lesson-11-streamable-http-transport.html',
        'lesson-12-streamable-http-deep-dive.html',
        'lesson-13-building-mcp-server.html',
        'lesson-14-mcp-inspector.html',
        'lesson-15-building-mcp-client.html',
        'lesson-16-sampling.html',
        'lesson-17-notifications.html',
        'lesson-18-roots.html',
        'lesson-19-transport-comparison-error-handling.html',
        'lesson-20-capstone-project.html',
    ]

    print(f"Processing {len(lessons)} lessons...")
    print(f"Adding Coding Practice tab with:")
    print(f"  - XP progress tracking")
    print(f"  - Solution reveal mechanism")
    print(f"  - Validation stubs")
    print()

    for lesson_file in lessons:
        file_path = melvin_dir / lesson_file
        if file_path.exists():
            add_practice_tab(file_path)
        else:
            print(f"  ⚠️  Skipping {lesson_file} - file not found")

    print()
    print("✅ Done! Coding Practice tabs added to all lessons.")
    print()
    print("Note: Exercises content is placeholder for now.")
    print("      Each lesson needs specific exercises designed per plan.")
    print()


if __name__ == '__main__':
    main()
