# Summary-Extraction
The repository consists of extracting summary from 10-K documents and Earning Call Transcripts (ECTs) of various companies across the financial years 2015-21.

The links to be used for reading the 10-K files are created using link_extraction.py file and then used in document_retrieval.py file for extracting the summary from item-16. The file document_extraction.py is used for downloading the raw html files for those documents which might have a summary in item-16 of 10-K documents.

Pegasus and BART models are used for generating summary of ECTs. We created a short summary for every paragraph which represents the dialogue exchanged between the operator and the members of the respective companies present during the meeting and merged those short summaries to form a complete summary for the text file.
