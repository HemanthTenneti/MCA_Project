#!/usr/bin/env python3
"""Generate the editable project guide from current recorded measurements.
Run with a Python environment containing python-docx (Codex bundled runtime used).
"""
import csv
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/project_guide.docx'


def element(tag, **attrs):
    e=OxmlElement(tag)
    for key,value in attrs.items(): e.set(qn(key), str(value))
    return e


def main():
    rows=list(csv.DictReader((ROOT/'reports/accuracy.csv').open()))
    loop={r['strategy']:r for r in rows if r['workload']=='repeated_loop'}
    verification=json.loads((ROOT/'reports/verification.json').read_text())
    units=json.loads((ROOT/'reports/unit_checks.json').read_text())
    synth=list(csv.DictReader((ROOT/'reports/synthesis/summary.csv').open()))
    labels={'always_not_taken':'Always not taken','one_bit':'1-bit predictor','two_bit':'2-bit predictor','fixture_reference':'Serial fixture reference'}
    doc=Document()
    section=doc.sections[0]
    section.page_width=Inches(8.27);section.page_height=Inches(11.69)
    section.top_margin=Inches(.68);section.bottom_margin=Inches(.65)
    section.left_margin=Inches(.72);section.right_margin=Inches(.72)
    section.header_distance=Inches(.26);section.footer_distance=Inches(.28)
    styles=doc.styles
    for name in ('Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption'):
        st=styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
        st._element.get_or_add_rPr().append(element('w:rFonts',**{'w:ascii':'Calibri','w:hAnsi':'Calibri'}))
    styles['Normal'].font.size=Pt(11)
    styles['Normal'].paragraph_format.line_spacing=1.12
    styles['Normal'].paragraph_format.space_after=Pt(8)
    styles['Title'].font.size=Pt(30);styles['Title'].font.bold=True
    styles['Title'].paragraph_format.space_after=Pt(12)
    styles['Subtitle'].font.italic=False;styles['Subtitle'].font.size=Pt(15);styles['Subtitle'].paragraph_format.space_after=Pt(14)
    styles['Heading 1'].font.size=Pt(22);styles['Heading 1'].font.bold=True
    styles['Heading 1'].paragraph_format.space_after=Pt(12)
    styles['Heading 2'].font.size=Pt(13);styles['Heading 2'].font.bold=True
    styles['Heading 2'].paragraph_format.space_before=Pt(12)
    styles['Heading 2'].paragraph_format.space_after=Pt(5)
    styles['Caption'].font.bold=False;styles['Caption'].font.size=Pt(9);styles['Caption'].font.italic=False
    styles['Caption'].paragraph_format.space_after=Pt(9)
    doc.core_properties.title='Dynamic Branch Prediction Unit Project Guide'
    doc.core_properties.subject='Project requirements and implementation'
    doc.core_properties.author='MCA Project Team'
    doc.core_properties.keywords='Verilog, branch prediction, MCA, requirements'
    hp=section.header.paragraphs[0];hp.text='MCA PROJECT 5     DYNAMIC BRANCH PREDICTION UNIT'
    hp.runs[0].font.size=Pt(8);hp.runs[0].font.color.rgb=RGBColor(0,0,0)
    fp=section.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=fp.add_run('Project requirements and implementation  |  ');r.font.size=Pt(8)
    fld=element('w:fldSimple',**{'w:instr':'PAGE'});fp._p.append(fld)

    def p(text='',bold_start=None):
        para=doc.add_paragraph()
        if bold_start and text.startswith(bold_start):
            para.add_run(bold_start).bold=True;para.add_run(text[len(bold_start):])
        else: para.add_run(text)
        return para
    def h(text):doc.add_heading(text,level=2)
    def page(text):doc.add_page_break();doc.add_heading(text,level=1)
    def code(text):
        para=doc.add_paragraph()
        para.paragraph_format.space_after=Pt(5)
        r=para.add_run(text);r.font.name='Courier New';r.font.size=Pt(10)
        return para
    def table(headers,data,widths):
        t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
        for c,width in zip(t.columns,widths):c.width=Inches(width)
        for i,text in enumerate(headers):t.rows[0].cells[i].text=str(text)
        t.rows[0]._tr.get_or_add_trPr().append(element('w:tblHeader'))
        for row in data:
            cells=t.add_row().cells
            for c,text in zip(cells,row):c.text=str(text)
        for ri,row in enumerate(t.rows):
            row._tr.get_or_add_trPr().append(element('w:cantSplit'))
            for ci,c in enumerate(row.cells):
                c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                props=c._tc.get_or_add_tcPr()
                borders=element('w:tcBorders')
                for edge in ('top','left','bottom','right'):
                    borders.append(element('w:'+edge,**{'w:val':'single','w:sz':4,'w:color':'D9D9D9'}))
                props.append(borders)
                margins=element('w:tcMar')
                for edge in ('top','bottom'):margins.append(element('w:'+edge,**{'w:w':90,'w:type':'dxa'}))
                for edge in ('left','right'):margins.append(element('w:'+edge,**{'w:w':110,'w:type':'dxa'}))
                props.append(margins)
                props.append(element('w:shd',**{'w:fill':'E8EEF6' if ri==0 else ('F7F9FC' if ri%2==0 else 'FFFFFF')}))
                for para in c.paragraphs:
                    para.paragraph_format.space_after=Pt(0);para.paragraph_format.line_spacing=1.05
                    if ci>0 and len(str(c.text))<22:para.alignment=WD_ALIGN_PARAGRAPH.CENTER
                    for run in para.runs:run.font.size=Pt(10);run.font.bold=ri==0;run.font.color.rgb=RGBColor(0,0,0)
        p().paragraph_format.space_after=Pt(0)
        return t
    def figure(name,caption,width=6.65):
        para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_after=Pt(2)
        shape=para.add_run().add_picture(str(ROOT/'reports/figures'/name),width=Inches(width))
        shape._inline.docPr.set('descr',caption)
        para.paragraph_format.keep_with_next=True
        doc.add_paragraph(caption,'Caption')
    def math_cpi():
        para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER
        omathp=element('m:oMathPara');omath=element('m:oMath')
        def term(parent,text):
            r=element('m:r');r.append(element('m:t'));r[-1].text=text;parent.append(r)
        term(omath,'CPI = 1 + ')
        fraction=element('m:f');num=element('m:num');den=element('m:den')
        term(num,'recoveries × 2');term(den,'1600');fraction.append(num);fraction.append(den);omath.append(fraction)
        omathp.append(omath);para._p.append(omathp)

    doc.add_paragraph('Dynamic Branch\nPrediction Unit','Title')
    doc.add_paragraph('Project requirements and implementation guide','Subtitle')
    p('This guide explains what our Modern Computer Architecture project asks us to build, how our Verilog implementation works, and how we demonstrate that it is correct. It is written for team members who need to understand and present the project without reading every source file first.')
    h('The project in one paragraph')
    p('A processor must choose which instruction to fetch next before every branch outcome is known. Our hardware predicts that choice, learns from resolved branches, and requests a flush and redirect when the saved prediction is wrong. We compare a simple baseline with two predictors that learn from past outcomes.')
    table(['Strategy','How it chooses a direction'],[
        ['Always not taken','Always continue to the next sequential instruction.'],
        ['1-bit predictor','Use the last outcome stored for the indexed branch.'],
        ['2-bit predictor','Use a saturating counter that tolerates an isolated outcome change.'],
    ],[1.65,5.10])
    h('What we chose to build')
    p('We implemented a standalone, synthesizable prediction unit with a branch-resolution test harness. Project 5 lists predictor RTL and evaluation deliverables, so a complete CPU is outside our chosen scope. The harness supplies known branch addresses and outcomes, saves the original prediction, and resolves each branch two cycles later.')
    h('Where to start')
    p('Run make demo for a short explanation in the terminal. Open reports/results.html for the visual comparison across all workloads. Use the remaining pages to understand the requirements, hardware, verification, and demonstration.')
    p('The measurements in this guide come from the project CSV and JSON evidence. CPI and FPGA frequency values are analytical or tool estimates; no physical board measurement is claimed.')

    page('Project requirements')
    p('The supplied brief defines Project 5 and a set of requirements common to all projects. The matrix below maps those requirements to our implementation. Module suggestions and example instructions in the brief guide the design without fixing its exact size or interface.')
    table(['Requirement from the brief','How our project meets it'],[
        ['Architecture diagram and explanation','The system diagram shows direction prediction, target storage, address selection, and recovery.'],
        ['State transition description','A four-state diagram explains the 2-bit counter, including both saturation boundaries.'],
        ['Modular synthesizable Verilog RTL','Separate modules implement the history table, target buffer, prediction selection, and recovery interface.'],
        ['Dedicated testbench and branch traces','Directed tests cover corner cases; ten deterministic workloads supply branch histories.'],
        ['Functional simulation and waveforms','Icarus runs the RTL; saved VCD files and a waveform preview expose signal timing.'],
        ['Accuracy and strategy comparison','All three strategies run identical traces and produce direction and next-address accuracy tables.'],
        ['Quantitative performance metric','Recovery counts and analytical CPI estimate the effect of wrong next-address predictions.'],
        ['Synthesis resources and maximum frequency','Yosys and nextpnr produce device-specific utilization and routed timing estimates.'],
        ['Final report and live demonstration','The technical report records evidence; the demo guide supplies a presentation sequence.'],
    ],[2.48,4.27])
    h('Design choices rather than course mandates')
    p('Our defaults are 32-bit addresses, 4-byte instructions, 64 history entries, 16 target entries, a two-cycle resolution delay, and a two-cycle recovery penalty in the CPI model. These are our practical implementation choices. The brief does not mandate these numbers.')
    p('We use BEQ and BNE examples, as suggested in the brief. Each outcome is derived from operand equality or inequality. FPGA implementation is suggested where hardware is available; our delivery uses simulation and synthesis without a physical board.')
    p('Source: Project_list_MCA.pdf, Project 5 on pages 3 and 4, and Common Project Requirements and tool flow on page 7, as inspected when the project was scoped.')

    page('How branch prediction works')
    p('The program counter, or PC, is the address of the current instruction. For our fixed 4-byte instruction format, ordinary sequential execution continues at PC + 4. A taken branch chooses a target address instead. BEQ is taken when two operands are equal; BNE is taken when they differ.')
    h('Direction and destination are separate questions')
    p('The history table predicts taken or not taken. The branch target buffer, or BTB, stores a destination. We use the target only when direction is taken and the BTB has a valid matching entry. Otherwise we predict PC + 4. This is why high direction accuracy alone does not guarantee a correct next address.')
    h('Why the second bit helps a repeated loop')
    p('A 1-bit entry changes to not taken at loop exit, so it often misses the next invocation\'s first taken branch. A 2-bit counter can remain weakly taken after one exit. Its prediction is the counter\'s most significant bit. Taken increments it; not taken decrements it; the value never wraps past either end.')
    figure('counter_states.png','The 2-bit counter resets to 01 and updates only on a valid resolved branch.')
    table(['Counter state','Prediction','If taken','If not taken'],[
        ['00  Strongly not taken','Not taken','01','00'],
        ['01  Weakly not taken','Not taken','10','00'],
        ['10  Weakly taken','Taken','11','01'],
        ['11  Strongly taken','Taken','11','10'],
    ],[2.60,1.35,1.35,1.45])
    p('An outcome can flip a weak state immediately; the predictor does not always need two misses to change direction. Its resistance to a single contrary outcome applies when it starts in a strong state. Alternating outcomes can defeat both dynamic predictors with our chosen reset states.')

    page('Our hardware design')
    figure('architecture.png','Prediction is saved at issue edge N and checked against the resolved next address at N+2.')
    h('The modules and their responsibilities')
    p('direction_predictor.v stores the 1-bit or 2-bit history, or implements the fixed baseline. The default index is PC bits 7 through 2. Entries have no tag, so addresses 256 bytes apart share a history entry and can interfere.')
    p('branch_target_buffer.v stores 16 valid bits, address tags, and target addresses. PC bits 5 through 2 select an entry. A taken resolution replaces that slot; a not-taken resolution leaves its target intact. Reset clears validity so uninitialized targets cannot be used.')
    p('branch_predictor.v combines direction and target lookup to choose the next PC. Its query interface receives a known branch PC and a valid signal. Its update interface receives the resolved PC, outcome, target, and update-valid signal.')
    p('branch_recovery.v compares the saved next PC with the actual next PC. A mismatch on a valid resolution asserts flush and supplies redirect_pc. The consumer should act on the redirect only when recovery is valid.')
    h('Timing and reset behavior')
    p('Reads are combinational and updates happen on a rising clock edge. Active-high synchronous reset has priority over updates. The harness holds the original prediction until resolution, even if the current table output changes. It allows one outstanding branch and does not execute a complete instruction pipeline.')

    page('How we implement and run it')
    h('Build the simplest working path first')
    p('Start with always not taken, a small branch trace, and a recovery counter. This verifies trace input, PC + 4 selection, and flush behavior before adding state. Then add the 1-bit table and extend it to a 2-bit saturating counter using the same query and update interface.')
    h('Add target lookup and check recovery')
    p('Connect the tagged target buffer and save prediction metadata at issue. At N+2, compare the actual next address with the saved choice, then train the tables. Test missing targets, collisions, changed targets, and disabled updates before collecting performance results.')
    h('Use identical traces for every strategy')
    p('The generator creates always-taken and not-taken patterns, repeated and nested loops, alternating outcomes, fixed-seed biased random branches, history and target collisions, changing targets, and operand edge cases. Each record includes the branch PC, operands, target, outcome, and count of preceding nonbranch instructions.')
    p('The Python model independently predicts each branch and checks every RTL field. Each workload starts cold. The target-change trace is an adversarial interface test; a changing target at one PC is not typical of direct BEQ or BNE code.')
    h('Run from the project folder')
    code('make all')
    p('Runs tests, lint, trace generation, RTL comparison, synthesis, figures, and both reports. Required tools are Icarus Verilog, Verilator, Yosys, nextpnr-ice40, Python, and the Matplotlib environment documented in README.md.')
    code('make demo')
    p('Prints the repeated-loop comparison and a readable visit-by-visit walkthrough.')
    code('python3 scripts/demo.py --details')
    p('Adds readable counter states, target hits, and saved next addresses.')
    code('make sim')
    p('Runs the simulation path and regenerates reports without rerunning synthesis. An existing hardware report is retained. Open reports/results.html in a browser to inspect all workloads offline.')

    page('What the results show')
    p('The repeated-loop workload runs 32 invocations of nine taken outcomes followed by one not-taken exit. That gives 320 branches in 1,600 retired instructions. The comparison below uses cold tables, base CPI 1, and two extra cycles per recovery.')
    table(['Strategy','Correct next PC','Recoveries','Estimated CPI'],[
        [labels[m],f"{float(loop[m]['next_address_accuracy']):.2%}",loop[m]['recoveries'],f"{float(loop[m]['estimated_cpi']):.5f}"]
        for m in ('always_not_taken','one_bit','two_bit')],[2.05,1.60,1.40,1.70])
    p('The baseline misses every taken outcome. The 1-bit predictor misses the first taken branch and the exit on every invocation. The 2-bit predictor misses the first training branch and each exit, giving 33 recoveries. It avoids 255 recoveries relative to the baseline on this workload.')
    math_cpi()
    p('This estimate counts recovery cost per retired instruction. General form: add base CPI to branch frequency multiplied by next-address miss rate and recovery penalty. The serialized harness cycle count must not be treated as measured CPU CPI.')
    h('Patterns that expose the limitations')
    p('On the alternating trace, always not taken gets 50% of next addresses correct; both dynamic predictors get 0% with our reset states. On target-buffer collisions, direction can be learned while next-address accuracy remains 0%, because the branches repeatedly evict each other\'s destinations.')
    h('Synthesis and timing estimates')
    table(['Wrapped configuration','Logic cells','RAM blocks','Estimated MHz'],[
        [labels[r['strategy']],r['logic_cells'],r['block_rams'],f"{float(r['estimated_fmax_mhz']):.2f}"] for r in synth],
        [2.65,1.25,1.20,1.65])
    p('Target: iCE40 HX8K CT256, seed 1, constraint 25 MHz. All configurations meet that constraint. Full designs include predictor, recovery, and registered serial transport. The fixture is a separate reference, not exact overhead to subtract. Frequencies are routed internal tool estimates, not physical-board measurements.')

    page('Verification and live demonstration')
    h('What the checks establish')
    p(f"The RTL matched the independent model on {verification['comparisons']:,} branch predictions across {verification['workloads']} workloads and {verification['strategies']} strategies. The comparison checks state, direction, target hit, predicted address, actual address, and flush for every recorded branch.")
    p(f"The directed RTL testbench passes 90 checks, and {units['python_tests']} hand-calculated Python tests check known behavior. Directed cases cover all counter transitions and saturation, reset priority, disabled updates, query validity, table indexing, collisions, target replacement, saved predictions, invalid resolution, and address wraparound.")
    p('A serial wrapper makes FPGA evaluation possible with five external signals. Three transactions test cold prediction, learning, and the absence of repeated updates. Those transactions also pass for every mapped predictor in post-synthesis functional simulation. This check is not exhaustive equivalence or timing simulation.')
    h('A short presentation sequence')
    for text in [
        '1. Explain the problem using the architecture diagram: choose the next address early and recover if it was wrong.',
        '2. Run make demo. Compare 288, 64, and 33 recoveries on the same repeated loop.',
        '3. Follow the first twelve visits. Point out the first exit and the following entry, where the 1-bit and 2-bit behavior differs.',
        '4. Open the visual results page. Show the alternating trace and target-buffer collisions so the audience sees the limits.',
        '5. Show the waveform and verification records. Finish with resource and timing estimates and explain what has been measured.',
    ]:p(text)
    h('Where the evidence lives')
    table(['Artifact','Location'],[
        ['Readable visual report','reports/results.html'],['Full technical report','reports/technical_report.md'],
        ['Accuracy and recovery data','reports/accuracy.csv'],['Verification records','reports/verification.json and reports/unit_checks.json'],
        ['Hardware and mapped checks','reports/synthesis/'],['Waveforms and signal list','reports/waveforms/ and docs/loop.gtkw'],
    ],[2.15,4.60])
    p('Requirements source: the supplied Project_list_MCA.pdf. Implementation details and figures: this project\'s RTL, tests, design notes, and measured CSV/JSON reports. No complete CPU, speculative rollback, multiple outstanding branches, or physical FPGA demonstration is included in this implementation.')
    OUT.parent.mkdir(exist_ok=True)
    # Remove inherited decorative title rules from the built-in document template.
    for tree in (doc.styles.element, doc._element):
        for border in tree.xpath('.//w:pBdr'):
            border.getparent().remove(border)
    doc.save(OUT)
    print(f'Created {OUT}')


if __name__=='__main__':main()
