use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

use std::collections::HashMap;
use std::ffi::CString;
use std::fmt;
use std::time::{Duration, Instant};

const PYPAGE_VERSION: &str = "2.2.1";

// Error types
#[derive(Debug)]
pub enum PypageError {
    SyntaxError(String),
    RuntimeError(String),
    IncompleteTagNode {
        open_delim: String,
        close_delim: String,
        line: usize,
        column: usize,
    },
    MultiLineBlockTag {
        line: usize,
        column: usize,
    },
    UnboundEndBlockTag {
        tag: String,
        line: usize,
        column: usize,
    },
    MismatchingEndBlockTag {
        expected: String,
        found: String,
        line: usize,
        column: usize,
    },
    MismatchingIndentation {
        line: usize,
        expected: String,
    },
    UnclosedTag {
        tag: String,
        line: usize,
        column: usize,
    },
    ExpressionMissing {
        tag: String,
        line: usize,
        column: usize,
    },
    ExpressionProhibited {
        tag: String,
        line: usize,
        column: usize,
    },
    ElifOrElseWithoutIf {
        line: usize,
        column: usize,
    },
    IncorrectForTag {
        src: String,
    },
    InvalidCaptureBlockVariableName {
        varname: String,
    },
    InvalidDefBlockFunctionOrArgName {
        name: String,
    },
    InvalidDefBlockMismatchingArgCount {
        expected: usize,
        found: usize,
    },
    UnknownTag {
        tag: String,
        line: usize,
        column: usize,
    },
    FileNotFound {
        filepath: String,
    },
    PythonError(PyErr),
}

impl fmt::Display for PypageError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PypageError::SyntaxError(msg) => write!(f, "Syntax Error: {}", msg),
            PypageError::RuntimeError(msg) => write!(f, "Error: {}", msg),
            PypageError::IncompleteTagNode {
                open_delim,
                close_delim,
                line,
                column,
            } => {
                write!(
                    f,
                    "Missing closing '{}' for opening '{}' at line {}, column {}.",
                    close_delim, open_delim, line, column
                )
            }
            PypageError::MultiLineBlockTag { line, column } => {
                write!(f, "The tag starting at line {}, column {}, spans multiple lines. This is not permitted. Block tags must be on one line.", line, column)
            }
            PypageError::UnboundEndBlockTag { tag, line, column } => {
                write!(
                    f,
                    "Unbound closing tag '{}' at line {}, column {}.",
                    tag, line, column
                )
            }
            PypageError::MismatchingEndBlockTag {
                expected,
                found,
                line,
                column,
            } => {
                write!(
                    f,
                    "The end tag '{}' at line {}, column {} should be '{}' instead.",
                    found, line, column, expected
                )
            }
            PypageError::MismatchingIndentation { line, expected } => {
                write!(
                    f,
                    "Mismatching indentation in line {}. Expected indentation: '{}'",
                    line, expected
                )
            }
            PypageError::UnclosedTag { tag, line, column } => {
                write!(
                    f,
                    "Missing closing tag for opening '{}' at line {}, column {}.",
                    tag, line, column
                )
            }
            PypageError::ExpressionMissing { tag, line, column } => {
                write!(
                    f,
                    "Expression missing in '{}' tag at line {}, column {}.",
                    tag, line, column
                )
            }
            PypageError::ExpressionProhibited { tag, line, column } => {
                write!(
                    f,
                    "The '{}' tag at line {}, column {}, must appear by itself.",
                    tag, line, column
                )
            }
            PypageError::ElifOrElseWithoutIf { line, column } => {
                write!(
                    f,
                    "Missing initial 'if' tag for conditional tag at line {}, column {}.",
                    line, column
                )
            }
            PypageError::IncorrectForTag { src } => {
                write!(f, "Incorrect 'for' tag syntax: '{}'", src)
            }
            PypageError::InvalidCaptureBlockVariableName { varname } => {
                write!(
                    f,
                    "Incorrect CaptureBlock: '{}' is not a valid Python variable name.",
                    varname
                )
            }
            PypageError::InvalidDefBlockFunctionOrArgName { name } => {
                write!(
                    f,
                    "Incorrect DefBlock: '{}' is not a valid function or argument name.",
                    name
                )
            }
            PypageError::InvalidDefBlockMismatchingArgCount { expected, found } => {
                write!(f, "Incorrect DefBlock function call: expected {} arguments but received {} instead.", expected, found)
            }
            PypageError::UnknownTag { tag, line, column } => {
                write!(
                    f,
                    "Unknown tag '{}' at line {}, column {}.",
                    tag, line, column
                )
            }
            PypageError::FileNotFound { filepath } => {
                write!(f, "File {} does not exist.", filepath)
            }
            PypageError::PythonError(err) => write!(f, "Python Error: {}", err),
        }
    }
}

impl From<PyErr> for PypageError {
    fn from(err: PyErr) -> Self {
        PypageError::PythonError(err)
    }
}

impl From<std::ffi::NulError> for PypageError {
    fn from(err: std::ffi::NulError) -> Self {
        PypageError::SyntaxError(format!("Null byte in string: {}", err))
    }
}

// Location in source code
#[derive(Debug, Clone, Copy)]
pub struct Location {
    pub line: usize,
    pub column: usize,
}

impl Location {
    pub fn new(line: usize, column: usize) -> Self {
        Self { line, column }
    }
}

// AST Node types
#[derive(Debug, Clone)]
pub enum Node<'a> {
    Root(RootNode<'a>),
    Text(TextNode<'a>),
    Code(CodeNode<'a>),
    Comment(CommentNode<'a>),
    Block(BlockNode<'a>),
}

#[derive(Debug, Clone)]
pub struct RootNode<'a> {
    pub children: Vec<Node<'a>>,
}

impl<'a> RootNode<'a> {
    pub fn new() -> Self {
        Self {
            children: Vec::new(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct TextNode<'a> {
    pub src: &'a str,
}

impl<'a> TextNode<'a> {
    pub fn new(src: &'a str) -> Self {
        Self { src }
    }
}

#[derive(Debug, Clone)]
pub struct CodeNode<'a> {
    pub src: &'a str,
    pub loc: Location,
}

impl<'a> CodeNode<'a> {
    pub fn new(src: &'a str, loc: Location) -> Self {
        Self { src, loc }
    }
}

#[derive(Debug, Clone)]
pub struct CommentNode<'a> {
    pub src: &'a str,
    pub loc: Location,
}

impl<'a> CommentNode<'a> {
    pub fn new(src: &'a str, loc: Location) -> Self {
        Self { src, loc }
    }
}

#[derive(Debug, Clone)]
pub enum BlockType<'a> {
    Conditional(ConditionalBlock<'a>),
    For(ForBlock),
    While(WhileBlock),
    Def(DefBlock),
    Capture(CaptureBlock),
    Comment(CommentBlock),
    End(EndBlock),
}

#[derive(Debug, Clone)]
pub struct BlockNode<'a> {
    pub src: &'a str,
    pub loc: Location,
    pub children: Vec<Node<'a>>,
    pub block_type: BlockType<'a>,
}

impl<'a> BlockNode<'a> {
    pub fn new(src: &'a str, loc: Location, block_type: BlockType<'a>) -> Self {
        Self {
            src,
            loc,
            children: Vec::new(),
            block_type,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ConditionalBlock<'a> {
    pub tag_type: ConditionalType,
    pub expr: String,
    pub continuation: Option<Box<BlockNode<'a>>>,
}

#[derive(Debug, Clone)]
pub enum ConditionalType {
    If,
    Elif,
    Else,
}

#[derive(Debug, Clone)]
pub struct ForBlock {
    pub targets: Vec<String>,
    pub genexpr: String,
}

#[derive(Debug, Clone)]
pub struct WhileBlock {
    pub expr: String,
    pub dofirst: bool,
    pub slow: bool,
}

#[derive(Debug, Clone)]
pub struct DefBlock {
    pub funcname: String,
    pub argnames: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct CaptureBlock {
    pub varname: String,
}

#[derive(Debug, Clone)]
pub struct CommentBlock;

#[derive(Debug, Clone)]
pub struct EndBlock {
    pub tag_to_end: String,
}

// Tag delimiters
const CODE_OPEN: &str = "{{";
const CODE_CLOSE: &str = "}}";
const COMMENT_OPEN: &str = "{#";
const COMMENT_CLOSE: &str = "#}";
const BLOCK_OPEN: &str = "{%";
const BLOCK_CLOSE: &str = "%}";

// Token types for lexing
#[derive(Debug, Clone)]
pub enum Token<'a> {
    Text(&'a str),
    Code { src: &'a str, loc: Location },
    Comment { src: &'a str, loc: Location },
    Block { src: &'a str, loc: Location },
}

// Helper enum to track token in progress during lexing
#[derive(Debug)]
enum TokenInProgress {
    None,
    Text(usize),              // start index
    Code(usize, Location),    // start index, location
    Comment(usize, Location), // start index, location
    Block(usize, Location),   // start index, location
}

pub fn unescape_str_cow(s: &str) -> std::borrow::Cow<str> {
    // Only allocate a new string if escaping is actually needed
    if !s.contains("\\{") && !s.contains("\\}") {
        return std::borrow::Cow::Borrowed(s);
    }
    std::borrow::Cow::Owned(s.replace("\\{", "{").replace("\\}", "}"))
}

pub fn is_identifier(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }

    let mut chars = s.chars();
    let first = chars.next().unwrap();

    if !first.is_alphabetic() && first != '_' {
        return false;
    }

    chars.all(|c| c.is_alphanumeric() || c == '_')
}

pub fn first_occurrence(text: &str, c: char) -> Option<usize> {
    text.find(c)
}

pub fn last_occurrence(text: &str, c: char) -> Option<usize> {
    text.rfind(c)
}

pub fn indent(text: &str, level: usize, width: usize) -> String {
    let prefix = " ".repeat(width * level);
    text.lines()
        .map(|line| format!("{}{}", prefix, line))
        .collect::<Vec<_>>()
        .join("\n")
}

fn matches_two_char_delim(c: char, next_char: Option<char>, delim: &str) -> bool {
    if let Some(next) = next_char {
        let delim_chars: Vec<char> = delim.chars().collect();
        if delim_chars.len() == 2 {
            return c == delim_chars[0] && next == delim_chars[1];
        }
    }
    false
}

// Lexer implementation
pub fn lex(src: &str) -> Result<Vec<Token>, PypageError> {
    let mut tokens = Vec::new();
    let mut current_token = TokenInProgress::None;
    let mut comment_tag_depth = 0;

    let mut line_number = 1;
    let mut newline_position = 0;
    let chars: Vec<(usize, char)> = src.char_indices().collect();
    let mut i = 0;

    while i < chars.len() {
        let (byte_pos, c) = chars[i];
        let next_char = if i + 1 < chars.len() {
            Some(chars[i + 1].1)
        } else {
            None
        };

        if c == '\n' {
            line_number += 1;
            newline_position = byte_pos;
        }
        let column_number = byte_pos - newline_position;
        let loc = Location::new(line_number, column_number);

        match current_token {
            TokenInProgress::None => {
                if matches_two_char_delim(c, next_char, CODE_OPEN) {
                    let start_pos = if i + 2 < chars.len() {
                        chars[i + 2].0
                    } else {
                        src.len()
                    };
                    current_token = TokenInProgress::Code(start_pos, loc);
                    i += 2;
                    continue;
                } else if matches_two_char_delim(c, next_char, COMMENT_OPEN) {
                    let start_pos = if i + 2 < chars.len() {
                        chars[i + 2].0
                    } else {
                        src.len()
                    };
                    current_token = TokenInProgress::Comment(start_pos, loc);
                    comment_tag_depth += 1;
                    i += 2;
                    continue;
                } else if matches_two_char_delim(c, next_char, BLOCK_OPEN) {
                    let start_pos = if i + 2 < chars.len() {
                        chars[i + 2].0
                    } else {
                        src.len()
                    };
                    current_token = TokenInProgress::Block(start_pos, loc);
                    i += 2;
                    continue;
                } else {
                    current_token = TokenInProgress::Text(byte_pos);
                }
            }
            TokenInProgress::Text(start) => {
                if matches_two_char_delim(c, next_char, CODE_OPEN)
                    || matches_two_char_delim(c, next_char, COMMENT_OPEN)
                    || matches_two_char_delim(c, next_char, BLOCK_OPEN)
                {
                    // Finish current text token
                    if byte_pos > start {
                        tokens.push(Token::Text(&src[start..byte_pos]));
                    }
                    // Start new token
                    let start_pos = if i + 2 < chars.len() {
                        chars[i + 2].0
                    } else {
                        src.len()
                    };
                    if matches_two_char_delim(c, next_char, CODE_OPEN) {
                        current_token = TokenInProgress::Code(start_pos, loc);
                    } else if matches_two_char_delim(c, next_char, COMMENT_OPEN) {
                        current_token = TokenInProgress::Comment(start_pos, loc);
                        comment_tag_depth += 1;
                    } else if matches_two_char_delim(c, next_char, BLOCK_OPEN) {
                        current_token = TokenInProgress::Block(start_pos, loc);
                    }
                    i += 2;
                    continue;
                } else {
                    i += 1;
                }
            }
            TokenInProgress::Code(start, start_loc) => {
                if matches_two_char_delim(c, next_char, CODE_CLOSE) {
                    tokens.push(Token::Code {
                        src: &src[start..byte_pos],
                        loc: start_loc,
                    });
                    current_token = TokenInProgress::None;
                    i += 2;
                    continue;
                } else {
                    i += 1;
                }
            }
            TokenInProgress::Comment(start, start_loc) => {
                if matches_two_char_delim(c, next_char, COMMENT_OPEN) {
                    comment_tag_depth += 1;
                    i += 2;
                    continue;
                } else if matches_two_char_delim(c, next_char, COMMENT_CLOSE) {
                    comment_tag_depth -= 1;
                    if comment_tag_depth == 0 {
                        tokens.push(Token::Comment {
                            src: &src[start..byte_pos],
                            loc: start_loc,
                        });
                        current_token = TokenInProgress::None;
                        i += 2;
                        continue;
                    } else {
                        i += 2;
                        continue;
                    }
                } else {
                    i += 1;
                }
            }
            TokenInProgress::Block(start, start_loc) => {
                if matches_two_char_delim(c, next_char, BLOCK_CLOSE) {
                    let block_src = &src[start..byte_pos];
                    if block_src.contains('\n') {
                        return Err(PypageError::MultiLineBlockTag {
                            line: start_loc.line,
                            column: start_loc.column,
                        });
                    }
                    tokens.push(Token::Block {
                        src: block_src,
                        loc: start_loc,
                    });
                    current_token = TokenInProgress::None;
                    i += 2;
                    continue;
                } else {
                    i += 1;
                }
            }
        }
    }

    // Handle remaining token
    match current_token {
        TokenInProgress::None => {}
        TokenInProgress::Text(start) => {
            if start < src.len() {
                tokens.push(Token::Text(&src[start..]));
            }
        }
        TokenInProgress::Code(_, loc) => {
            return Err(PypageError::IncompleteTagNode {
                open_delim: CODE_OPEN.to_owned(),
                close_delim: CODE_CLOSE.to_owned(),
                line: loc.line,
                column: loc.column,
            });
        }
        TokenInProgress::Comment(_, loc) => {
            return Err(PypageError::IncompleteTagNode {
                open_delim: COMMENT_OPEN.to_owned(),
                close_delim: COMMENT_CLOSE.to_owned(),
                line: loc.line,
                column: loc.column,
            });
        }
        TokenInProgress::Block(_, loc) => {
            return Err(PypageError::IncompleteTagNode {
                open_delim: BLOCK_OPEN.to_owned(),
                close_delim: BLOCK_CLOSE.to_owned(),
                line: loc.line,
                column: loc.column,
            });
        }
    }

    Ok(tokens)
}

// Continue with parser and other functions...

// Parser implementation
pub fn parse_block_type(src: &str, loc: Location) -> Result<BlockType, PypageError> {
    let unescaped = unescape_str_cow(src);
    let trimmed = unescaped.trim();

    if trimmed.is_empty() || trimmed.starts_with("end") {
        let tag_to_end = if trimmed.starts_with("end") {
            trimmed[3..].trim().to_string()
        } else {
            String::new()
        };
        return Ok(BlockType::End(EndBlock { tag_to_end }));
    }

    if trimmed == "comment" {
        return Ok(BlockType::Comment(CommentBlock));
    }

    if trimmed.starts_with("if ") || trimmed.starts_with("elif ") || trimmed == "else" {
        let (tag_type, expr_str) = if trimmed.starts_with("if ") {
            (ConditionalType::If, trimmed[3..].trim())
        } else if trimmed.starts_with("elif ") {
            (ConditionalType::Elif, trimmed[5..].trim())
        } else {
            (ConditionalType::Else, "True")
        };

        if matches!(tag_type, ConditionalType::Else) && !expr_str.is_empty() && expr_str != "True" {
            return Err(PypageError::ExpressionProhibited {
                tag: "else".to_string(),
                line: loc.line,
                column: loc.column,
            });
        }

        if expr_str.is_empty() && !matches!(tag_type, ConditionalType::Else) {
            let tag_name = match tag_type {
                ConditionalType::If => "if",
                ConditionalType::Elif => "elif",
                ConditionalType::Else => "else",
            };
            return Err(PypageError::ExpressionMissing {
                tag: tag_name.to_string(),
                line: loc.line,
                column: loc.column,
            });
        }

        return Ok(BlockType::Conditional(ConditionalBlock {
            tag_type,
            expr: expr_str.to_string(),
            continuation: None,
        }));
    }

    if trimmed.starts_with("for ") {
        let targets = find_for_targets(&trimmed)?;
        let genexpr = format!("(({}) {})", targets.join(", "), trimmed);
        return Ok(BlockType::For(ForBlock { targets, genexpr }));
    }

    if trimmed.starts_with("while ") {
        let mut expr_str = trimmed[6..].trim();
        let mut dofirst = false;
        let mut slow = false;

        if expr_str.starts_with("dofirst ") {
            dofirst = true;
            expr_str = expr_str[8..].trim();
        }

        if expr_str.ends_with(" slow") {
            slow = true;
            expr_str = expr_str[..expr_str.len() - 5].trim();
        }

        return Ok(BlockType::While(WhileBlock {
            expr: expr_str.to_string(),
            dofirst,
            slow,
        }));
    }

    if trimmed.starts_with("def ") {
        let parts: Vec<&str> = trimmed[4..].trim().split_whitespace().collect();
        if parts.is_empty() {
            return Err(PypageError::InvalidDefBlockFunctionOrArgName {
                name: "".to_string(),
            });
        }

        for part in &parts {
            if !is_identifier(part) {
                return Err(PypageError::InvalidDefBlockFunctionOrArgName {
                    name: part.to_string(),
                });
            }
        }

        let funcname = parts[0].to_string();
        let argnames = parts[1..].iter().map(|s| s.to_string()).collect();

        return Ok(BlockType::Def(DefBlock { funcname, argnames }));
    }

    if trimmed.starts_with("capture ") {
        let varname = trimmed[8..].trim().to_string();
        if !is_identifier(&varname) {
            return Err(PypageError::InvalidCaptureBlockVariableName { varname });
        }
        return Ok(BlockType::Capture(CaptureBlock { varname }));
    }

    Err(PypageError::UnknownTag {
        tag: trimmed.to_string(),
        line: loc.line,
        column: loc.column,
    })
}

fn find_for_targets(src: &str) -> Result<Vec<String>, PypageError> {
    let mut targets = Vec::new();
    let tokens: Vec<&str> = src.split_whitespace().collect();

    // Only process the first 'for' loop, not nested ones
    for i in 0..tokens.len() {
        if tokens[i] == "for" && i + 2 < tokens.len() {
            let for_pos = i;
            if let Some(in_pos) = tokens[for_pos + 1..].iter().position(|&x| x == "in") {
                let in_pos = for_pos + 1 + in_pos;
                let target_list = &tokens[for_pos + 1..in_pos];

                for target in target_list {
                    // Only collect clean characters if needed
                    let needs_cleaning = target
                        .chars()
                        .any(|c| !(c.is_alphanumeric() || c == '_' || c == ','));

                    if needs_cleaning {
                        let clean_target: String = target
                            .chars()
                            .filter(|c| c.is_alphanumeric() || *c == '_' || *c == ',')
                            .collect();

                        for t in clean_target.split(',') {
                            let t = t.trim();
                            if is_identifier(t) && !targets.iter().any(|existing| existing == t) {
                                targets.push(t.to_string());
                            }
                        }
                    } else {
                        for t in target.split(',') {
                            let t = t.trim();
                            if is_identifier(t) && !targets.iter().any(|existing| existing == t) {
                                targets.push(t.to_string());
                            }
                        }
                    }
                }

                // Only process the first 'for' loop, then break
                break;
            }
        }
    }

    if targets.is_empty() {
        return Err(PypageError::IncorrectForTag {
            src: src.to_string(),
        });
    }

    targets.sort();
    Ok(targets)
}

pub fn prune_tokens(tokens: Vec<Token>) -> Vec<Token> {
    // For now, just filter out empty text tokens
    tokens
        .into_iter()
        .filter(|token| match token {
            Token::Text(text) => !text.is_empty(),
            _ => true,
        })
        .collect()
}

// Token queue wrapper that allows putting tokens back
struct TokenQueue<'a> {
    tokens: std::iter::Peekable<std::vec::IntoIter<Token<'a>>>,
    queue: Vec<Token<'a>>,
}

impl<'a> TokenQueue<'a> {
    fn new(tokens: std::iter::Peekable<std::vec::IntoIter<Token<'a>>>) -> Self {
        Self {
            tokens,
            queue: Vec::new(),
        }
    }

    fn next(&mut self) -> Option<Token<'a>> {
        if let Some(token) = self.queue.pop() {
            Some(token)
        } else {
            self.tokens.next()
        }
    }

    fn peek(&mut self) -> Option<&Token<'a>> {
        if self.queue.is_empty() {
            self.tokens.peek()
        } else {
            self.queue.last()
        }
    }

    fn put_back(&mut self, token: Token<'a>) {
        self.queue.push(token);
    }
}

enum StopReason<'a> {
    EndOfTokens,
    EndTag(Token<'a>),
    Continuation(Token<'a>),
}

fn build_conditional_chain<'a>(
    block_node: &mut BlockNode<'a>,
    tokens: &mut TokenQueue<'a>,
) -> Result<(), PypageError> {
    // Build children for this block
    let stop_reason = build_tree_for_block_with_reason(block_node, tokens)?;

    // Handle continuations based on the stop reason
    if let StopReason::Continuation(continuation_token) = stop_reason {
        if let Token::Block { src, loc } = continuation_token {
            let block_type = parse_block_type(src, loc)?;
            if let BlockType::Conditional(ref cond) = block_type {
                if matches!(cond.tag_type, ConditionalType::Elif | ConditionalType::Else) {
                    let mut continuation_block = BlockNode::new(src, loc, block_type);

                    // Recursively build the continuation chain
                    build_conditional_chain(&mut continuation_block, tokens)?;

                    // Attach as continuation
                    if let BlockType::Conditional(ref mut main_cond) = block_node.block_type {
                        main_cond.continuation = Some(Box::new(continuation_block));
                    }
                }
            }
        }
    } else if let StopReason::EndTag(end_token) = stop_reason {
        // Put the end tag back for the parent to handle
        tokens.put_back(end_token);
    }

    Ok(())
}

fn build_tree_for_block_with_reason<'a>(
    block_node: &mut BlockNode<'a>,
    tokens: &mut TokenQueue<'a>,
) -> Result<StopReason<'a>, PypageError> {
    while let Some(token) = tokens.next() {
        match token {
            Token::Text(text) => {
                block_node.children.push(Node::Text(TextNode::new(text)));
            }
            Token::Code { src, loc } => {
                block_node
                    .children
                    .push(Node::Code(CodeNode::new(src, loc)));
            }
            Token::Comment { src: _, loc: _ } => {
                // Comments are ignored
            }
            Token::Block { src, loc } => {
                let block_type = parse_block_type(src, loc)?;

                if let BlockType::End(end_block) = block_type {
                    // This is an end tag - check if it matches our current block
                    let matches_current = if end_block.tag_to_end.is_empty() {
                        // Generic end tag - matches any block
                        true
                    } else {
                        // Specific end tag - check if it matches current block
                        match &block_node.block_type {
                            BlockType::Conditional(_) => end_block.tag_to_end == "if",
                            BlockType::For(_) => end_block.tag_to_end == "for",
                            BlockType::While(_) => end_block.tag_to_end == "while",
                            BlockType::Def(_) => end_block.tag_to_end == "def",
                            BlockType::Capture(_) => end_block.tag_to_end == "capture",
                            BlockType::Comment(_) => end_block.tag_to_end == "comment",
                            BlockType::End(_) => false,
                        }
                    };

                    if matches_current {
                        return Ok(StopReason::EndOfTokens);
                    } else {
                        // End tag doesn't match - return it for parent to handle
                        return Ok(StopReason::EndTag(Token::Block { src, loc }));
                    }
                }

                // Check if this is a continuation block (elif/else)
                if let BlockType::Conditional(ref cond) = block_type {
                    if matches!(cond.tag_type, ConditionalType::Elif | ConditionalType::Else) {
                        // This is a continuation - return it
                        return Ok(StopReason::Continuation(Token::Block { src, loc }));
                    }
                }

                let mut child_block = BlockNode::new(src, loc, block_type);

                // Build children for this child block recursively
                if let BlockType::Conditional(_) = child_block.block_type {
                    build_conditional_chain(&mut child_block, tokens)?;
                } else {
                    let stop_reason = build_tree_for_block_with_reason(&mut child_block, tokens)?;
                    // If the child stopped due to an end tag or continuation, we need to handle it
                    if let StopReason::EndTag(end_token) = stop_reason {
                        tokens.put_back(end_token);
                    } else if let StopReason::Continuation(cont_token) = stop_reason {
                        tokens.put_back(cont_token);
                    }
                }

                block_node.children.push(Node::Block(child_block));
            }
        }
    }
    Ok(StopReason::EndOfTokens)
}

fn build_tree_for_block<'a>(
    block_node: &mut BlockNode<'a>,
    tokens: &mut TokenQueue<'a>,
) -> Result<(), PypageError> {
    let stop_reason = build_tree_for_block_with_reason(block_node, tokens)?;
    // Handle any remaining tokens
    if let StopReason::EndTag(end_token) = stop_reason {
        tokens.put_back(end_token);
    } else if let StopReason::Continuation(cont_token) = stop_reason {
        tokens.put_back(cont_token);
    }
    Ok(())
}

pub fn build_tree<'a>(
    parent: &mut Node<'a>,
    tokens: &mut TokenQueue<'a>,
) -> Result<(), PypageError> {
    while let Some(token) = tokens.next() {
        match token {
            Token::Text(text) => {
                let text_node = Node::Text(TextNode::new(text));
                match parent {
                    Node::Root(ref mut root) => root.children.push(text_node),
                    Node::Block(ref mut block) => block.children.push(text_node),
                    _ => {
                        return Err(PypageError::SyntaxError(
                            "Invalid parent for text node".to_string(),
                        ))
                    }
                }
            }
            Token::Code { src, loc } => {
                let code_node = Node::Code(CodeNode::new(src, loc));
                match parent {
                    Node::Root(ref mut root) => root.children.push(code_node),
                    Node::Block(ref mut block) => block.children.push(code_node),
                    _ => {
                        return Err(PypageError::SyntaxError(
                            "Invalid parent for code node".to_string(),
                        ))
                    }
                }
            }
            Token::Comment { src: _, loc: _ } => {
                // Comments are ignored
            }
            Token::Block { src, loc } => {
                let block_type = parse_block_type(src, loc)?;

                if let BlockType::End(end_block) = block_type {
                    // This is an end tag - should only return if we're in a block context
                    if let Node::Block(ref parent_block) = parent {
                        if end_block.tag_to_end.is_empty() {
                            // Generic end tag - matches any block
                            return Ok(());
                        } else {
                            // Specific end tag - check if it matches current block
                            let matches = match &parent_block.block_type {
                                BlockType::Conditional(_) => end_block.tag_to_end == "if",
                                BlockType::For(_) => end_block.tag_to_end == "for",
                                BlockType::While(_) => end_block.tag_to_end == "while",
                                BlockType::Def(_) => end_block.tag_to_end == "def",
                                BlockType::Capture(_) => end_block.tag_to_end == "capture",
                                BlockType::Comment(_) => end_block.tag_to_end == "comment",
                                BlockType::End(_) => false,
                            };

                            if matches {
                                return Ok(());
                            } else {
                                // End tag doesn't match - put it back and return
                                tokens.put_back(Token::Block { src, loc });
                                return Ok(());
                            }
                        }
                    } else {
                        // We're at root level - this is an unbound end tag
                        return Err(PypageError::UnboundEndBlockTag {
                            tag: format!("end{}", end_block.tag_to_end),
                            line: loc.line,
                            column: loc.column,
                        });
                    }
                }

                let mut block_node = BlockNode::new(src, loc, block_type);

                // Handle conditional continuation
                if let BlockType::Conditional(ref cond) = block_node.block_type {
                    if matches!(cond.tag_type, ConditionalType::Elif | ConditionalType::Else) {
                        // This should be handled by the parent conditional
                        if let Node::Block(ref mut parent_block) = parent {
                            if let BlockType::Conditional(ref mut parent_cond) =
                                parent_block.block_type
                            {
                                // Build children for this continuation block
                                build_tree_for_block(&mut block_node, tokens)?;
                                parent_cond.continuation = Some(Box::new(block_node));
                                return Ok(());
                            }
                        }
                        return Err(PypageError::ElifOrElseWithoutIf {
                            line: loc.line,
                            column: loc.column,
                        });
                    }
                }

                // Build children for this block and handle continuations recursively
                if let BlockType::Conditional(_) = block_node.block_type {
                    build_conditional_chain(&mut block_node, tokens)?;
                } else {
                    build_tree_for_block(&mut block_node, tokens)?;
                }

                match parent {
                    Node::Root(ref mut root) => root.children.push(Node::Block(block_node)),
                    Node::Block(ref mut block) => block.children.push(Node::Block(block_node)),
                    _ => {
                        return Err(PypageError::SyntaxError(
                            "Invalid parent for block node".to_string(),
                        ))
                    }
                }
            }
        }
    }
    Ok(())
}

pub fn parse(src: &str) -> Result<Node, PypageError> {
    let tokens = lex(src)?;
    let tokens = prune_tokens(tokens);

    let mut tree = Node::Root(RootNode::new());
    let mut token_queue = TokenQueue::new(tokens.into_iter().peekable());
    build_tree(&mut tree, &mut token_queue)?;

    Ok(tree)
}

// Python execution engine
pub struct PypageExec<'py> {
    py: Python<'py>,
    globals: Bound<'py, PyDict>,
}

impl<'py> PypageExec<'py> {
    pub fn new(py: Python<'py>, seed_env: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let globals = PyDict::new(py);

        // Set up built-in variables
        globals.set_item("__package__", py.None())?;
        globals.set_item("__name__", "pypage_code")?;
        globals.set_item("__doc__", py.None())?;

        // Add any seed environment
        if let Some(env) = seed_env {
            for (key, value) in env.iter() {
                globals.set_item(key, value)?;
            }
        }

        Ok(Self { py, globals })
    }

    pub fn run_code(&self, code: &str, _loc: Location) -> Result<String, PypageError> {
        let unescaped_code = unescape_str_cow(code);
        let trimmed_code = unescaped_code.trim();
        let code_cstring = CString::new(trimmed_code)?;

        // Try to evaluate as expression first
        match self.py.eval(&code_cstring, Some(&self.globals), None) {
            Ok(result) => {
                let result_str = result.str()?.to_string();
                Ok(if result_str == "None" {
                    String::new()
                } else {
                    result_str
                })
            }
            Err(_) => {
                // If evaluation fails, try execution
                self.py.run(&code_cstring, Some(&self.globals), None)?;
                Ok(String::new())
            }
        }
    }

    pub fn eval_expression(&self, expr: &str) -> Result<bool, PypageError> {
        let code_cstring = CString::new(expr)?;
        let result = self.py.eval(&code_cstring, Some(&self.globals), None)?;
        Ok(result.is_truthy()?)
    }

    pub fn get_global(&self, name: &str) -> Option<String> {
        self.globals
            .get_item(name)
            .ok()
            .flatten()
            .and_then(|v| v.str().ok())
            .map(|s| s.to_string())
    }

    pub fn set_global(&self, name: &str, value: &str) -> PyResult<()> {
        self.globals.set_item(name, value)
    }

    pub fn set_global_object(&self, name: &str, obj: &Bound<'py, PyAny>) -> PyResult<()> {
        self.globals.set_item(name, obj)
    }

    pub fn has_global(&self, name: &str) -> bool {
        self.globals.contains(name).unwrap_or(false)
    }

    pub fn backup_globals(&self, names: &[String]) -> HashMap<String, Bound<'py, PyAny>> {
        let mut backup = HashMap::new();
        for name in names {
            if let Ok(Some(value)) = self.globals.get_item(name) {
                backup.insert(name.clone(), value);
            }
        }
        backup
    }

    pub fn restore_globals(&self, backup: HashMap<String, Bound<'py, PyAny>>) -> PyResult<()> {
        for (name, value) in backup {
            self.globals.set_item(name, value)?;
        }
        Ok(())
    }

    pub fn delete_globals(&self, names: &[String]) -> PyResult<()> {
        for name in names {
            if self.has_global(name) {
                self.globals.del_item(name)?;
            }
        }
        Ok(())
    }

    pub fn eval_as_object(&self, expr: &str) -> Result<Bound<'py, PyAny>, PypageError> {
        let code_cstring = CString::new(expr)?;
        let result = self.py.eval(&code_cstring, Some(&self.globals), None)?;
        Ok(result)
    }
}

pub fn exec_tree<'py, 'a>(node: &Node<'a>, exec: &PypageExec<'py>) -> Result<String, PypageError> {
    match node {
        Node::Root(root) => {
            let mut output = String::new();
            for child in &root.children {
                output.push_str(&exec_tree(child, exec)?);
            }
            Ok(output)
        }
        Node::Text(text) => Ok(text.src.to_owned()),
        Node::Code(code) => exec.run_code(code.src, code.loc),
        Node::Comment(_) => Ok(String::new()),
        Node::Block(block) => {
            match &block.block_type {
                BlockType::Conditional(cond) => {
                    if exec.eval_expression(&cond.expr)? {
                        let mut output = String::new();
                        for child in &block.children {
                            output.push_str(&exec_tree(child, exec)?);
                        }
                        Ok(output)
                    } else if let Some(continuation) = &cond.continuation {
                        exec_tree(&Node::Block((**continuation).clone()), exec)
                    } else {
                        Ok(String::new())
                    }
                }
                BlockType::For(for_block) => {
                    let mut output = String::new();

                    // Backup any conflicting variables
                    let backup = exec.backup_globals(&for_block.targets);

                    // Evaluate the generator expression
                    let generator = exec.eval_as_object(&for_block.genexpr)?;

                    // Iterate over the generator
                    loop {
                        // Call next() on the generator
                        match generator.call_method0("__next__") {
                            Ok(result) => {
                                // Set target variables based on the result
                                if for_block.targets.len() == 1 {
                                    // Single target variable
                                    exec.set_global_object(&for_block.targets[0], &result)?;
                                } else {
                                    // Multiple target variables - unpack the result
                                    // First, check if the result is iterable (tuple, list, etc.)
                                    if let Ok(result_iter) = result.try_iter() {
                                        // Use iterator to unpack
                                        let values: Vec<Bound<'_, PyAny>> =
                                            result_iter.collect::<PyResult<Vec<_>>>()?;
                                        for (i, target) in for_block.targets.iter().enumerate() {
                                            if i < values.len() {
                                                exec.set_global_object(target, &values[i])?;
                                            }
                                        }
                                    } else {
                                        // Try to extract as tuple/list
                                        let result_tuple =
                                            result.extract::<Vec<Bound<'_, PyAny>>>()?;
                                        for (i, target) in for_block.targets.iter().enumerate() {
                                            if i < result_tuple.len() {
                                                exec.set_global_object(target, &result_tuple[i])?;
                                            }
                                        }
                                    }
                                }

                                // Execute the loop body
                                for child in &block.children {
                                    output.push_str(&exec_tree(child, exec)?);
                                }
                            }
                            Err(_) => {
                                // StopIteration - end of loop
                                break;
                            }
                        }
                    }

                    // Clean up target variables and restore backups
                    exec.delete_globals(&for_block.targets)?;
                    exec.restore_globals(backup)?;

                    Ok(output)
                }
                BlockType::While(while_block) => {
                    let mut output = String::new();

                    // Execute once first if dofirst is true
                    if while_block.dofirst {
                        for child in &block.children {
                            output.push_str(&exec_tree(child, exec)?);
                        }
                    }

                    // Set up time limit for non-slow loops
                    let loop_start_time = Instant::now();
                    let time_limit = Duration::from_secs_f64(2.0); // 2 seconds
                    let mut iteration_count = 0;
                    let max_iterations = 10000; // Prevent runaway loops

                    // Main loop
                    while exec.eval_expression(&while_block.expr)? {
                        // Execute the loop body
                        for child in &block.children {
                            output.push_str(&exec_tree(child, exec)?);
                        }

                        iteration_count += 1;

                        // Check time limit for non-slow loops
                        if !while_block.slow {
                            if loop_start_time.elapsed() > time_limit {
                                eprintln!(
                                    "Loop '{}' terminated after {} iterations (time limit).",
                                    while_block.expr, iteration_count
                                );
                                break;
                            }
                            if iteration_count >= max_iterations {
                                eprintln!(
                                    "Loop '{}' terminated after {} iterations ({} iteration limit).",
                                    while_block.expr, iteration_count, max_iterations
                                );
                                break;
                            }
                        }
                    }

                    Ok(output)
                }
                BlockType::Def(def_block) => {
                    // For now, create a simple Python function that validates arguments
                    // In a full implementation, this would need to execute the block children
                    // with the bound arguments, but that requires more complex callback mechanisms

                    let func_code = format!(
                        r#"
def {}(*args):
    if len(args) != {}:
        raise ValueError("Function '{}' expects {} arguments, got {{}}".format(len(args)))
    # Function definitions are not fully implemented in this version
    return ""
"#,
                        def_block.funcname,
                        def_block.argnames.len(),
                        def_block.funcname,
                        def_block.argnames.len()
                    );

                    // Execute the function definition in Python
                    let func_cstring = CString::new(func_code.trim())?;
                    exec.py.run(&func_cstring, Some(&exec.globals), None)?;

                    Ok(String::new())
                }
                BlockType::Capture(capture_block) => {
                    let mut output = String::new();
                    for child in &block.children {
                        output.push_str(&exec_tree(child, exec)?);
                    }
                    exec.set_global(&capture_block.varname, &output)?;
                    Ok(String::new())
                }
                BlockType::Comment(_) => Ok(String::new()),
                BlockType::End(_) => Ok(String::new()),
            }
        }
    }
}

#[pyfunction]
pub fn pypage_process(source: &str, seed_env: Option<&Bound<'_, PyDict>>) -> PyResult<String> {
    Python::with_gil(|py| {
        let tree = parse(source)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let exec = PypageExec::new(py, seed_env)?;
        let result = exec_tree(&tree, &exec)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(result)
    })
}

#[pyfunction]
pub fn pypage_version() -> &'static str {
    PYPAGE_VERSION
}

/// A Python module implemented in Rust.
#[pymodule]
fn pypage(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pypage_process, m)?)?;
    m.add_function(wrap_pyfunction!(pypage_version, m)?)?;
    Ok(())
}
