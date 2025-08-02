# LinkedIn EasyApply Automation Tool

An automated tool that allows users to apply to multiple LinkedIn jobs using the EasyApply feature with just their LinkedIn credentials.

## Features

- 🚀 **One-Click Mass Application**: Apply to multiple jobs automatically
- 🎯 **Smart Job Filtering**: Automatically filters for EasyApply-enabled jobs
- 📊 **Detailed Reporting**: Generates comprehensive reports of applications sent
- 🔍 **Customizable Search**: Search by keywords, location, and job type
- 📝 **Logging**: Detailed logs of all activities and errors
- ⚡ **Rate Limiting**: Built-in delays to avoid being flagged

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (will be managed automatically)
- LinkedIn account

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd linkedIn-job-api
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Download ChromeDriver (optional - webdriver-manager will handle this):
   - The tool uses webdriver-manager to automatically download and manage ChromeDriver
   - No manual setup required!

## Usage

### Basic Usage

Run the main script:
```bash
python linkedin_easyapply.py
```

The tool will prompt you for:
- LinkedIn email address
- LinkedIn password
- Job search keywords (optional)
- Location (optional)
- Maximum number of applications to send

### Advanced Usage

You can also use the tool programmatically:

```python
from linkedin_easyapply import LinkedInEasyApply

# Create automation instance
automation = LinkedInEasyApply()

# Run automation with custom parameters
automation.run_automation(
    email="your-email@example.com",
    password="your-password",
    keywords="Python Developer",
    location="New York",
    max_applications=25
)
```

## Configuration

### Search Parameters

- **Keywords**: Job titles, skills, or company names
- **Location**: City, state, or "Remote"
- **Max Applications**: Limit the number of applications (default: 50)

### Safety Features

- **Rate Limiting**: 3-second delay between applications
- **Error Handling**: Continues even if individual applications fail
- **Logging**: All activities logged to `linkedin_automation.log`
- **User-Agent Rotation**: Mimics real browser behavior

## Output Files

The tool generates several output files:

1. **`application_report.json`**: Detailed JSON report of all applications
2. **`linkedin_automation.log`**: Comprehensive log file
3. **Console output**: Real-time progress and summary

### Sample Report Structure

```json
{
  "total_applied": 15,
  "total_failed": 3,
  "applied_jobs": [
    {
      "url": "https://linkedin.com/jobs/view/123456",
      "title": "Senior Python Developer",
      "status": "Applied"
    }
  ],
  "failed_jobs": [
    {
      "url": "https://linkedin.com/jobs/view/789012",
      "title": "Data Scientist",
      "status": "Failed"
    }
  ]
}
```

## Important Notes

### LinkedIn Terms of Service
- This tool automates interactions with LinkedIn
- Use responsibly and in accordance with LinkedIn's Terms of Service
- Consider the impact on your LinkedIn account
- LinkedIn may implement rate limiting or CAPTCHA challenges

### Best Practices
- **Start Small**: Begin with a low number of applications (5-10) to test
- **Review Applications**: Manually review some applications to ensure quality
- **Update Profile**: Ensure your LinkedIn profile is complete and up-to-date
- **Customize Resume**: Upload a relevant resume to your LinkedIn profile

### Limitations
- Only works with EasyApply jobs
- May not work with jobs requiring additional questions or uploads
- Success depends on your profile completeness
- LinkedIn's anti-bot measures may interfere

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify credentials are correct
   - Check if 2FA is enabled (currently not supported)
   - LinkedIn may require manual verification

2. **No Jobs Found**
   - Broaden search criteria
   - Check if location is spelled correctly
   - Ensure EasyApply filter is working

3. **Applications Failing**
   - Profile may be incomplete
   - Some jobs require additional information
   - Rate limiting may be in effect

### Error Logs
Check `linkedin_automation.log` for detailed error information.

## Security Considerations

- **Never commit credentials** to version control
- Consider using environment variables for credentials
- Be aware that this tool stores credentials in memory during execution
- Use at your own risk - LinkedIn may flag automated behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Disclaimer

This tool is for educational and personal use only. The authors are not responsible for any consequences resulting from the use of this tool. Users should comply with LinkedIn's Terms of Service and use the tool responsibly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log files
3. Create an issue in the repository

---

**⚠️ Warning**: Use this tool responsibly. Excessive automation may result in LinkedIn account restrictions.
