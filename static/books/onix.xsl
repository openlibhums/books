<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Output in HTML format -->
    <xsl:output method="html" encoding="UTF-8" indent="yes" />

    <!-- Root template -->
    <xsl:template match="/">
        <html>
            <head>
                <title>ONIX Book Export</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    h1 { color: #4CAF50; }
                    .book { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
                    .section-title { font-weight: bold; color: #333; }
                    .contributor { margin-left: 15px; }
                </style>
            </head>
            <body>
                <h1>ONIX Book Export</h1>
                <xsl:apply-templates select="ONIXMessage/Product" />
            </body>
        </html>
    </xsl:template>

    <!-- Template for each book -->
    <xsl:template match="Product">
        <div class="book">
            <h2>
                <xsl:value-of select="DescriptiveDetail/TitleDetail/TitleElement/TitleWithoutPrefix" />
            </h2>

            <!-- ISBN -->
            <p class="section-title">ISBN:</p>
            <p><xsl:value-of select="ProductIdentifier[ProductIDType='15']/IDValue" /></p>

            <!-- Contributors -->
            <p class="section-title">Contributors:</p>
            <xsl:for-each select="DescriptiveDetail/Contributor">
                <div class="contributor">
                    <strong><xsl:value-of select="NamesBeforeKey" /> <xsl:value-of select="KeyNames" /></strong>
                    <p>Role: <xsl:value-of select="ContributorRole" /></p>
                    <p>Bio: <xsl:value-of select="BiographicalNote" /></p>
                </div>
            </xsl:for-each>

            <!-- Book Description -->
            <p class="section-title">Description:</p>
            <p><xsl:value-of select="CollateralDetail/TextContent/Text" disable-output-escaping="yes" /></p>

            <!-- Publishing Details -->
            <p class="section-title">Publishing Details:</p>
            <p>Publisher: <xsl:value-of select="PublishingDetail/Publisher/PublisherName" /></p>
            <p>Location: <xsl:value-of select="PublishingDetail/CityOfPublication" /></p>
            <p>Date Published: <xsl:value-of select="PublishingDetail/PublishingDate/Date" /></p>
        </div>
    </xsl:template>
</xsl:stylesheet>
