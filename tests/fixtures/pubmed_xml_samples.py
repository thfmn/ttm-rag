"""
Sample XML data for testing PubMed XML parsing.

This file contains sample XML data from the PubMed API that we can use
to test our XML parsing functions.
"""

# Simple PubMed XML sample with basic fields
SIMPLE_PUBMED_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2023//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_230101.dtd">
<PubmedArticleSet>
<PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
        <PMID Version="1">12345678</PMID>
        <Article PubModel="Print">
            <Journal>
                <ISSN IssnType="Print">0028-4793</ISSN>
                <JournalIssue CitedMedium="Print">
                    <Volume>390</Volume>
                    <Issue>4</Issue>
                    <PubDate>
                        <Year>2023</Year>
                        <Month>Jun</Month>
                        <Day>15</Day>
                    </PubDate>
                </JournalIssue>
                <Title>The New England journal of medicine</Title>
            </Journal>
            <ArticleTitle>Traditional Medicine in Modern Healthcare</ArticleTitle>
            <Pagination>
                <MedlinePgn>1234-1241</MedlinePgn>
            </Pagination>
            <ELocationID EIdType="doi">10.1056/NEJMra2345678</ELocationID>
            <Abstract>
                <AbstractText>This article discusses the integration of traditional medicine practices into modern healthcare systems.</AbstractText>
            </Abstract>
            <AuthorList CompleteYN="Y">
                <Author ValidYN="Y">
                    <LastName>Smith</LastName>
                    <ForeName>John A</ForeName>
                    <AffiliationInfo>
                        <Affiliation>Department of Medicine, University Hospital</Affiliation>
                    </AffiliationInfo>
                </Author>
                <Author ValidYN="Y">
                    <LastName>Johnson</LastName>
                    <ForeName>Sarah B</ForeName>
                    <AffiliationInfo>
                        <Affiliation>Institute of Traditional Medicine, University of Health Sciences</Affiliation>
                    </AffiliationInfo>
                </Author>
            </AuthorList>
            <Language>eng</Language>
            <PublicationTypeList>
                <PublicationType UI="D016428">Journal Article</PublicationType>
                <PublicationType UI="D016454">Review</PublicationType>
            </PublicationTypeList>
            <VernacularTitle></VernacularTitle>
        </Article>
        <MedlineJournalInfo>
            <Country>United States</Country>
            <MedlineTA>N Engl J Med</MedlineTA>
            <NlmUniqueID>0255562</NlmUniqueID>
            <ISSNLinking>0028-4793</ISSNLinking>
        </MedlineJournalInfo>
        <ChemicalList>
            <Chemical>
                <NameOfSubstance UI="D000076">Plant Extracts</NameOfSubstance>
            </Chemical>
            <Chemical>
                <NameOfSubstance UI="D000602">Analgesics</NameOfSubstance>
            </Chemical>
        </ChemicalList>
        <MeshHeadingList>
            <MeshHeading>
                <DescriptorName UI="D000076" MajorTopicYN="N">Plant Extracts</DescriptorName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName UI="D000602" MajorTopicYN="N">Analgesics</DescriptorName>
            </MeshHeading>
            <MeshHeading>
                <DescriptorName UI="D000069575" MajorTopicYN="Y">Medicine, Traditional</DescriptorName>
            </MeshHeading>
        </MeshHeadingList>
    </MedlineCitation>
    <PubmedData>
        <History>
            <PubMedPubDate PubStatus="pubmed">
                <Year>2023</Year>
                <Month>6</Month>
                <Day>16</Day>
                <Hour>6</Hour>
                <Minute>0</Minute>
            </PubMedPubDate>
        </History>
        <PublicationStatus>ppublish</PublicationStatus>
        <ArticleIdList>
            <ArticleId IdType="pubmed">12345678</ArticleId>
            <ArticleId IdType="doi">10.1056/NEJMra2345678</ArticleId>
        </ArticleIdList>
    </PubmedData>
</PubmedArticle>
</PubmedArticleSet>'''

# Minimal PubMed XML sample with only required fields
MINIMAL_PUBMED_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2023//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_230101.dtd">
<PubmedArticleSet>
<PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
        <PMID Version="1">87654321</PMID>
        <Article PubModel="Print">
            <Journal>
                <Title>Journal of Medical Research</Title>
            </Journal>
            <ArticleTitle>Research on Medical Treatments</ArticleTitle>
        </Article>
    </MedlineCitation>
</PubmedArticle>
</PubmedArticleSet>'''

# PubMed XML sample with invalid PMID
INVALID_PMID_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2023//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_230101.dtd">
<PubmedArticleSet>
<PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
        <PMID Version="1">invalid123</PMID>
        <Article PubModel="Print">
            <Journal>
                <Title>Journal of Medical Research</Title>
            </Journal>
            <ArticleTitle>Research on Medical Treatments</ArticleTitle>
        </Article>
    </MedlineCitation>
</PubmedArticle>
</PubmedArticleSet>'''