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
pub enum Node {
    Root(RootNode),
    Text(TextNode),
    Code(CodeNode),
    Comment(CommentNode),
    Block(BlockNode),
}

#[derive(Debug, Clone)]
pub struct RootNode {
    pub children: Vec<Node>,
}

impl RootNode {
    pub fn new() -> Self {
        Self {
            children: Vec::new(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct TextNode {
    pub src: String,
}

impl TextNode {
    pub fn new() -> Self {
        Self { src: String::new() }
    }
}

#[derive(Debug, Clone)]
pub struct CodeNode {
    pub src: String,
    pub loc: Location,
}

impl CodeNode {
    pub fn new(loc: Location) -> Self {
        Self {
            src: String::new(),
            loc,
        }
    }
}

#[derive(Debug, Clone)]
pub struct CommentNode {
    pub src: String,
    pub loc: Location,
}

impl CommentNode {
    pub fn new(loc: Location) -> Self {
        Self {
            src: String::new(),
            loc,
        }
    }
}

#[derive(Debug, Clone)]
pub enum BlockType {
    Conditional(ConditionalBlock),
    For(ForBlock),
    While(WhileBlock),
    Def(DefBlock),
    Capture(CaptureBlock),
    Comment(CommentBlock),
    End(EndBlock),
}

#[derive(Debug, Clone)]
pub struct BlockNode {
    pub src: String,
    pub loc: Location,
    pub children: Vec<Node>,
    pub block_type: BlockType,
}

impl BlockNode {
    pub fn new(loc: Location, block_type: BlockType) -> Self {
        Self {
            src: String::new(),
            loc,
            children: Vec::new(),
            block_type,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ConditionalBlock {
    pub tag_type: ConditionalType,
    pub expr: String,
    pub continuation: Option<Box<BlockNode>>,
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
pub enum Token {
    Text(String),
    Code { src: String, loc: Location },
    Comment { src: String, loc: Location },
    Block { src: String, loc: Location },
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

// Lexer implementation
pub fn lex(src: &str) -> Result<Vec<Token>, PypageError> {
    let mut tokens = Vec::new();
    let mut current_token: Option<Token> = None;
    let mut comment_tag_depth = 0;

    let mut i = 0;
    let mut line_number = 1;
    let mut newline_position = 0;
    let chars: Vec<char> = src.chars().collect();

    while i < chars.len() {
        let c = chars.get(i).copied().unwrap_or('\0');
        let c2 = if i + 1 < chars.len() {
            format!("{}{}", c, chars.get(i + 1).copied().unwrap_or('\0'))
        } else {
            c.to_string()
        };

        if c == '\n' {
            line_number += 1;
            newline_position = i;
        }
        let column_number = i - newline_position;
        let loc = Location::new(line_number, column_number);

        // If we don't have a current token, look for tag delimiters
        if current_token.is_none() {
            if c2 == CODE_OPEN {
                current_token = Some(Token::Code {
                    src: String::new(),
                    loc,
                });
                i += 2;
                continue;
            } else if c2 == COMMENT_OPEN {
                current_token = Some(Token::Comment {
                    src: String::new(),
                    loc,
                });
                comment_tag_depth += 1;
                i += 2;
                continue;
            } else if c2 == BLOCK_OPEN {
                current_token = Some(Token::Block {
                    src: String::new(),
                    loc,
                });
                i += 2;
                continue;
            } else {
                current_token = Some(Token::Text(String::new()));
            }
        }

        match &mut current_token {
            Some(Token::Text(ref mut src)) => {
                if c2 == CODE_OPEN || c2 == COMMENT_OPEN || c2 == BLOCK_OPEN {
                    tokens.push(current_token.take().unwrap());
                    // Start new token
                    if c2 == CODE_OPEN {
                        current_token = Some(Token::Code {
                            src: String::new(),
                            loc,
                        });
                    } else if c2 == COMMENT_OPEN {
                        current_token = Some(Token::Comment {
                            src: String::new(),
                            loc,
                        });
                        comment_tag_depth += 1;
                    } else if c2 == BLOCK_OPEN {
                        current_token = Some(Token::Block {
                            src: String::new(),
                            loc,
                        });
                    }
                    i += 2;
                    continue;
                } else {
                    src.push(c);
                    i += 1;
                }
            }
            Some(Token::Code {
                ref mut src,
                loc: _,
            }) => {
                if c2 == CODE_CLOSE {
                    tokens.push(current_token.take().unwrap());
                    i += 2;
                    continue;
                } else if c2 == "\\{" {
                    src.push('{');
                    i += 2;
                    continue;
                } else if c2 == "\\}" {
                    src.push('}');
                    i += 2;
                    continue;
                } else {
                    src.push(c);
                    i += 1;
                }
            }
            Some(Token::Comment {
                ref mut src,
                loc: _,
            }) => {
                if c2 == COMMENT_OPEN {
                    comment_tag_depth += 1;
                    src.push_str(&c2);
                    i += 2;
                    continue;
                } else if c2 == COMMENT_CLOSE {
                    comment_tag_depth -= 1;
                    if comment_tag_depth == 0 {
                        tokens.push(current_token.take().unwrap());
                        i += 2;
                        continue;
                    } else {
                        src.push_str(&c2);
                        i += 2;
                        continue;
                    }
                } else {
                    src.push(c);
                    i += 1;
                }
            }
            Some(Token::Block { ref mut src, loc }) => {
                if c2 == BLOCK_CLOSE {
                    if src.contains('\n') {
                        return Err(PypageError::MultiLineBlockTag {
                            line: loc.line,
                            column: loc.column,
                        });
                    }
                    tokens.push(current_token.take().unwrap());
                    i += 2;
                    continue;
                } else if c2 == "\\{" {
                    src.push('{');
                    i += 2;
                    continue;
                } else if c2 == "\\}" {
                    src.push('}');
                    i += 2;
                    continue;
                } else {
                    src.push(c);
                    i += 1;
                }
            }
            None => unreachable!(),
        }
    }

    // Handle remaining token
    if let Some(token) = current_token {
        match &token {
            Token::Text(_) => tokens.push(token),
            Token::Code { loc, .. } | Token::Comment { loc, .. } | Token::Block { loc, .. } => {
                let open_delim = match token {
                    Token::Code { .. } => CODE_OPEN,
                    Token::Comment { .. } => COMMENT_OPEN,
                    Token::Block { .. } => BLOCK_OPEN,
                    _ => unreachable!(),
                };
                let close_delim = match token {
                    Token::Code { .. } => CODE_CLOSE,
                    Token::Comment { .. } => COMMENT_CLOSE,
                    Token::Block { .. } => BLOCK_CLOSE,
                    _ => unreachable!(),
                };
                return Err(PypageError::IncompleteTagNode {
                    open_delim: open_delim.to_string(),
                    close_delim: close_delim.to_string(),
                    line: loc.line,
                    column: loc.column,
                });
            }
        }
    }

    Ok(tokens)
}

// Continue with parser and other functions...

// Parser implementation
pub fn parse_block_type(src: &str, loc: Location) -> Result<BlockType, PypageError> {
    let trimmed = src.trim();

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
        let (tag_type, expr) = if trimmed.starts_with("if ") {
            (ConditionalType::If, trimmed[3..].trim().to_string())
        } else if trimmed.starts_with("elif ") {
            (ConditionalType::Elif, trimmed[5..].trim().to_string())
        } else {
            (ConditionalType::Else, "True".to_string())
        };

        if matches!(tag_type, ConditionalType::Else) && !expr.is_empty() && expr != "True" {
            return Err(PypageError::ExpressionProhibited {
                tag: "else".to_string(),
                line: loc.line,
                column: loc.column,
            });
        }

        if expr.is_empty() && !matches!(tag_type, ConditionalType::Else) {
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
            expr,
            continuation: None,
        }));
    }

    if trimmed.starts_with("for ") {
        let targets = find_for_targets(trimmed)?;
        let genexpr = format!("(({}) {})", targets.join(", "), trimmed);
        return Ok(BlockType::For(ForBlock { targets, genexpr }));
    }

    if trimmed.starts_with("while ") {
        let mut expr = trimmed[6..].trim().to_string();
        let mut dofirst = false;
        let mut slow = false;

        if expr.starts_with("dofirst ") {
            dofirst = true;
            expr = expr[8..].trim().to_string();
        }

        if expr.ends_with(" slow") {
            slow = true;
            expr = expr[..expr.len() - 5].trim().to_string();
        }

        return Ok(BlockType::While(WhileBlock {
            expr,
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

    let mut i = 0;
    while i < tokens.len() {
        if tokens[i] == "for" && i + 2 < tokens.len() {
            let for_pos = i;
            if let Some(in_pos) = tokens[for_pos + 1..].iter().position(|&x| x == "in") {
                let in_pos = for_pos + 1 + in_pos;
                let target_list: Vec<&str> = tokens[for_pos + 1..in_pos].iter().cloned().collect();

                for target in target_list {
                    let clean_target: String = target
                        .chars()
                        .filter(|c| c.is_alphanumeric() || *c == '_' || *c == ',')
                        .collect();

                    for t in clean_target.split(',') {
                        let t = t.trim();
                        if is_identifier(t) {
                            if !targets.contains(&t.to_string()) {
                                targets.push(t.to_string());
                            }
                        }
                    }
                }
                i = in_pos + 1;
            } else {
                break;
            }
        } else {
            i += 1;
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

fn build_conditional_chain(
    block_node: &mut BlockNode,
    tokens: &mut std::iter::Peekable<std::vec::IntoIter<Token>>,
) -> Result<(), PypageError> {
    // Build children for this block
    match build_tree_for_block(block_node, tokens) {
        Ok(()) => {
            // Normal completion, no continuation
        }
        Err(PypageError::SyntaxError(msg)) if msg.starts_with("CONTINUATION:") => {
            // Extract the continuation token information
            let parts: Vec<&str> = msg.split(':').collect();
            if parts.len() >= 3 {
                let cont_src = parts[1].to_string();
                let cont_line: usize = parts[2].parse().unwrap_or(0);
                let cont_loc = Location::new(cont_line, 0);

                // Parse the continuation block
                let cont_block_type = parse_block_type(&cont_src, cont_loc)?;
                let mut continuation_block = BlockNode::new(cont_loc, cont_block_type);
                continuation_block.src = cont_src;

                // Recursively build the continuation chain
                build_conditional_chain(&mut continuation_block, tokens)?;

                // Attach as continuation
                if let BlockType::Conditional(ref mut main_cond) = block_node.block_type {
                    main_cond.continuation = Some(Box::new(continuation_block));
                }
            }
        }
        Err(e) => return Err(e),
    }
    Ok(())
}

fn build_tree_for_block(
    block_node: &mut BlockNode,
    tokens: &mut std::iter::Peekable<std::vec::IntoIter<Token>>,
) -> Result<(), PypageError> {
    while let Some(token) = tokens.next() {
        match token {
            Token::Text(text) => {
                block_node.children.push(Node::Text(TextNode { src: text }));
            }
            Token::Code { src, loc } => {
                block_node.children.push(Node::Code(CodeNode { src, loc }));
            }
            Token::Comment { src: _, loc: _ } => {
                // Comments are ignored
            }
            Token::Block { src, loc } => {
                let block_type = parse_block_type(&src, loc)?;

                if let BlockType::End(_end_block) = block_type {
                    // This is an end tag, we should return
                    return Ok(());
                }

                let mut child_block = BlockNode::new(loc, block_type);
                child_block.src = src.clone();

                // Handle conditional continuation (elif/else) - this is a special case
                // We need to return this information to the caller so it can be handled
                // as a continuation of the parent conditional block
                if let BlockType::Conditional(ref cond) = child_block.block_type {
                    if matches!(cond.tag_type, ConditionalType::Elif | ConditionalType::Else) {
                        // This should be handled as a continuation - signal it
                        return Err(PypageError::SyntaxError(format!(
                            "CONTINUATION:{}:{}",
                            src, loc.line
                        )));
                    }
                }

                // Build children for this child block recursively
                if let BlockType::Conditional(_) = child_block.block_type {
                    build_conditional_chain(&mut child_block, tokens)?;
                } else {
                    build_tree_for_block(&mut child_block, tokens)?;
                }

                block_node.children.push(Node::Block(child_block));
            }
        }
    }
    Ok(())
}

pub fn build_tree(
    parent: &mut Node,
    tokens: &mut std::iter::Peekable<std::vec::IntoIter<Token>>,
) -> Result<(), PypageError> {
    while let Some(token) = tokens.next() {
        match token {
            Token::Text(text) => {
                let text_node = Node::Text(TextNode { src: text });
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
                let code_node = Node::Code(CodeNode { src, loc });
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
                let block_type = parse_block_type(&src, loc)?;

                if let BlockType::End(_end_block) = block_type {
                    // This is an end tag, we should return
                    return Ok(());
                }

                let mut block_node = BlockNode::new(loc, block_type);
                block_node.src = src.clone();

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
    let mut token_iter = tokens.into_iter().peekable();
    build_tree(&mut tree, &mut token_iter)?;

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
        let trimmed_code = code.trim();
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

pub fn exec_tree<'py>(node: &Node, exec: &PypageExec<'py>) -> Result<String, PypageError> {
    match node {
        Node::Root(root) => {
            let mut output = String::new();
            for child in &root.children {
                output.push_str(&exec_tree(child, exec)?);
            }
            Ok(output)
        }
        Node::Text(text) => Ok(text.src.clone()),
        Node::Code(code) => exec.run_code(&code.src, code.loc),
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

                    // Main loop
                    while exec.eval_expression(&while_block.expr)? {
                        // Execute the loop body
                        for child in &block.children {
                            output.push_str(&exec_tree(child, exec)?);
                        }

                        // Check time limit for non-slow loops
                        if !while_block.slow && loop_start_time.elapsed() > time_limit {
                            eprintln!("Loop '{}' terminated.", while_block.expr);
                            break;
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
