/*
  ==============================================================================

    This file contains the basic startup code for a JUCE application.

  ==============================================================================
*/

#include <JuceHeader.h>
#include <cairo/cairo.h>
#include <cairo/cairo-pdf.h>

//==============================================================================
int main (int argc, char* argv[])
{
    const juce::File output (juce::File::getSpecialLocation (juce::File::currentExecutableFile).getSiblingFile ("test.pdf"));

    if (output.existsAsFile())
        output.deleteFile();

    // Creating a cairo PDF Surface
    cairo_surface_t *csurface = cairo_pdf_surface_create(output.getFullPathName().toRawUTF8(), 500, 400);
    // Creating a cairo context
    cairo_t *ctx = cairo_create(csurface);
    // Creating rectangle in PDF
    cairo_rectangle(ctx, 0.0, 0.0, 400, 300);
    // Changing rectangle bacground color to Blue
    cairo_set_source_rgb(ctx, 0.0, 0.0, 0.5);
    cairo_fill(ctx);
    // Moving to (10, 10) position in PDF
    cairo_move_to(ctx, 10.0, 10.0);
    // Changing text color to Yellow
    cairo_set_source_rgb(ctx, 1.0, 1.0, 0.0);
    // Writing some text to PDF
    cairo_show_text(ctx, "This is a test");
    cairo_show_page(ctx);
    // Destroying cairo context
    cairo_destroy(ctx);
    cairo_surface_flush(csurface);
    // Destroying PDF surface
    cairo_surface_destroy(csurface);

    output.startAsProcess();

    return 0;
}
